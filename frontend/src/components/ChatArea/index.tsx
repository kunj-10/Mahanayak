"use client"
import { Chat } from "@/components/Chat"
import { useState, useEffect } from "react"
import { FiSend } from 'react-icons/fi'
import { useCopilotChat } from "@copilotkit/react-core"
import { Role, TextMessage } from "@copilotkit/runtime-client-gql";

// Define the message type
type Message = {
  message: string
  role: string
}

export const ChatArea = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState<string>("")

  // CopilotKit integration
  const {
    visibleMessages,
    appendMessage,
    isLoading
  } = useCopilotChat()

  // Sync CopilotKit messages with your existing message format
  useEffect(() => {
    const formattedMessages: Message[] = visibleMessages.map(msg => ({
      message: msg.content,
      role: msg.role
    }))
    setMessages(formattedMessages)
  }, [visibleMessages])

  const sendMessage = async () => {
    const trimmed = input.trim()
    if (trimmed === "" || isLoading) return
    
    await appendMessage( new TextMessage({
      content: trimmed,
      role: Role.User
    }))
    
    setInput("")
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="h-full w-full flex flex-col px-[15%] pt-2">

      <div className="flex h-[85%] overflow-auto sleek-scrollbar rounded mb-2 p-4">
        <Chat className="h-full w-full" messages={messages} isLoading={isLoading}/>
      </div>

      <div className="flex rounded-2xl h-[13%] mb-[4%] p-4 bg-gray-900">
        <textarea
          className="w-full h-full resize-none text-white outline-none p-2 sleek-scrollbar bg-transparent"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || input.trim() === ""}
          className="ml-2 h-[70%] my-auto aspect-square flex items-center justify-center bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-white"
          aria-label="Send"
        >
          <FiSend className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
}