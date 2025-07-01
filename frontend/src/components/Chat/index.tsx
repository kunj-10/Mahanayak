"use client"

import { useEffect, useRef, useState } from "react"
import { MessageBox } from "../MessageBox"

export const Chat = ({
  className,
  messages,
  isLoading
}: {
  className?: string
  messages: { message: string; role: string }[]
  isLoading: Boolean
}) => {
  const bottomRef = useRef<HTMLDivElement | null>(null)
  const [showLoading, setShowLoading] = useState<boolean>(false);
  const [loadingMsg, setLoadingMessage] = useState<string>("AI is Responding...");


  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className={`p-4 w-full ${className} overflow-auto no-scrollbar`}>
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className="mb-4 p-3 rounded bg-gray-800 text-white"
        >
          <MessageBox content={msg} setLoadingMessage={setLoadingMessage} setShowLoading={setShowLoading}/>
        </div>
      ))}
      {(isLoading || showLoading) && (
        <div className="mb-2 p-2 bg-blue-900/20 text-blue-200 rounded text-sm">
          {loadingMsg}
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  )
}
