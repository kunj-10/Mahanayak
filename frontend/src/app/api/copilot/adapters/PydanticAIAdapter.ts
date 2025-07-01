import {
  CopilotServiceAdapter,
  CopilotRuntimeChatCompletionRequest,
  CopilotRuntimeChatCompletionResponse,
} from "@copilotkit/runtime";
import { randomUUID } from "@copilotkit/shared";

interface PydanticAIMessage {
  role: string;
  content: string;
}

interface PydanticAIRequest {
  user_input: PydanticAIMessage[];
  chat_id: string;
  event?: string;
  event_id?: string;
  stream?: boolean;
  max_tokens?: number;
  temperature?: number;
  stop?: string[];
}

interface PydanticAIStreamChunk {
  id: string;
  choices: Array<{
    delta: {
      content?: string;
      role?: string;
    };
    finish_reason?: string;
  }>;
}

interface PydanticAIResponse {
  id: string;
  choices: Array<{
    message: {
      role: string;
      content: string;
      ui_component?: any;
    };
    finish_reason: string;
  }>;
}

export interface PydanticAIAdapterParams {
  /**
   * The base URL for your PydanticAI API
   */
  baseUrl: string;

  /**
   * Optional API key for authentication
   */
  apiKey?: string;

  /**
   * The model to use (if your PydanticAI backend supports multiple models)
   */
  model?: string;

  /**
   * Callback for handling UI components from PydanticAI responses
   */
  onUIComponent?: (component: any) => void;
}

export class PydanticAIAdapter implements CopilotServiceAdapter {
  private baseUrl: string;
  private apiKey?: string;
  private model?: string;
  private onUIComponent?: (component: any) => void;

  constructor(params: PydanticAIAdapterParams) {
    this.baseUrl = params.baseUrl.replace(/\/$/, '');
    this.apiKey = params.apiKey;
    this.onUIComponent = params.onUIComponent;
  }

  async process(
    request: CopilotRuntimeChatCompletionRequest,
  ): Promise<CopilotRuntimeChatCompletionResponse> {
    const {
      threadId: threadIdFromRequest,
      messages,
      eventSource,
      forwardedParameters,
    } = request;

    const threadId = threadIdFromRequest ?? randomUUID();

    // Convert CopilotKit messages to PydanticAI format
    const lastUserMessage = messages.findLast((m) => m.role === "user")?.content;

    if (!lastUserMessage) {
      throw new Error("No user message found to send to organiser backend.");
    }

    const requestBody: PydanticAIRequest = {
      user_input: lastUserMessage,
      chat_id: threadId,
      event_id: "68543e17caea5fd995970d0e",
      stream: true,
      max_tokens: forwardedParameters?.maxTokens || 1000,
      temperature: forwardedParameters?.temperature || 0.7,
      ...(forwardedParameters?.stop && { stop: forwardedParameters.stop }),
    };

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    try {
      console.log(`${this.baseUrl}/organiser_agent`)
      const response = await fetch(`${this.baseUrl}/organiser_agent`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`PydanticAI API error: ${response.status} ${response.statusText}`);
      }

      // Handle streaming response
      eventSource.stream(async (eventStream$) => {
        let messageId: string | null = null;
        let accumulatedContent = '';

        try {
          if (!response.body) {
            throw new Error('No response body for streaming');
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();

          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              eventStream$.complete();
              break;
            }
            
            const chunk = decoder.decode(value, { stream: true });
            console.log("[Streaming Chunk]", chunk);
            console.log("Type of chunk:", typeof chunk);

            try {
              const parsed = JSON.parse(chunk); // parse the full chunk directly

              const content = parsed.content;
              if (!content) return;

              if (!messageId) {
                messageId = parsed.id || randomUUID();
                if(messageId)
                eventStream$.sendTextMessageStart({ messageId });
              }

              if(parsed.type != "bot") accumulatedContent += content;

              if(messageId)
              eventStream$.sendTextMessageContent({
                messageId,
                content: chunk,
              });

              // Optional: handle completion/finish logic
              if (parsed.finish_reason) {
                if(messageId)
                eventStream$.sendTextMessageEnd({ messageId });
                messageId = null;
              }
            } catch (err) {
              console.warn("Invalid chunk received:", chunk);
              console.log(err)
            }
          }
          console.log("Out of Loop")
          console.log(accumulatedContent)
          
          reader.releaseLock();
        } catch (error) {
          console.error('[PydanticAI] Error processing stream:', error);
          
          // End any ongoing message
          if (messageId) {
            eventStream$.sendTextMessageEnd({ messageId });
          }
          
          throw error;
        }
      });
    } catch (error) {
      console.error('[PydanticAI] Error during API call:', error);
      throw error;
    }

    return {
      threadId,
    };
  }

  private async handleUIComponents(content: string): Promise<void> {
    // This method handles UI components if they're embedded in the response
    // You might need to adjust this based on how your PydanticAI backend
    // returns UI components
    try {
      // Example: If UI components are returned as JSON at the end of content
      const lines = content.split('\n');
      for (const line of lines) {
        if (line.startsWith('UI_COMPONENT:')) {
          const componentData = JSON.parse(line.slice(13));
          if (this.onUIComponent) {
            this.onUIComponent(componentData);
          }
        }
      }
    } catch (error) {
      // Ignore UI component parsing errors
      console.warn('[PydanticAI] Could not parse UI components:', error);
    }
  }

  private convertRole(role: string): string {
    // Map CopilotKit roles to standard chat roles
    switch (role.toLowerCase()) {
      case 'user':
        return 'user';
      case 'assistant':
        return 'assistant';
      case 'system':
        return 'system';
      default:
        return 'user';
    }
  }
}

// Global store for UI components
class UIComponentStore {
  private listeners: Array<(component: any) => void> = [];
  
  subscribe(listener: (component: any) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
  
  emit(component: any) {
    this.listeners.forEach(listener => listener(component));
  }
}

export const uiComponentStore = new UIComponentStore();

// Factory function to create PydanticAI runtime
export function createPydanticAIRuntime(config: PydanticAIAdapterParams) {
  const pydanticAdapter = new PydanticAIAdapter({
    ...config,
    onUIComponent: (component) => {
      // Emit UI component to subscribers
      uiComponentStore.emit(component);
      
      // Also call the provided callback if any
      if (config.onUIComponent) {
        config.onUIComponent(component);
      }
    },
  });

  return pydanticAdapter;
}

// Example usage:
// const adapter = createPydanticAIRuntime({
//   baseUrl: process.env.PYDANTIC_API_URL || 'http://localhost:8000',
//   apiKey: process.env.PYDANTIC_API_KEY,
//   model: 'your-model-name', // optional
//   onUIComponent: (component) => {
//     console.log('Received UI component:', component);
//   },
// });
//
// const runtime = new CopilotRuntime({
//   serviceAdapter: adapter,
// });