import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
} from '@copilotkit/runtime';
import { NextRequest } from 'next/server';
import { createPydanticAIRuntime } from "./adapters/PydanticAIAdapter"; 

const serviceAdapter = createPydanticAIRuntime({
  baseUrl: process.env.PYDANTIC_API_URL || 'http://127.0.0.1:8000/api',
  onUIComponent: (component) => {
    console.log('Received UI component:', component);
  },
});

const runtime = new CopilotRuntime();

export const POST = async (req: NextRequest) => {
  console.log("Hello")
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: '/api/copilot',
  });
 
  return handleRequest(req);
};