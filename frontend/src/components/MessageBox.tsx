"use client"

import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const MessageBox = ({
  content,
  setLoadingMessage,
  setShowLoading,
}: {
  content: { message: string; role: string };
  setLoadingMessage: React.Dispatch<React.SetStateAction<string>>;
  setShowLoading: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  const [msg, setMsg] = useState<string>("");

  useEffect(() => {
    console.log(content);
    if (typeof content?.message === 'string') {
      const rawMatches = content.message.match(/{[^]*?}/g) || [];
      setMsg("");
      
      rawMatches.forEach((str) => {
        try {
          let parsed = JSON.parse(str);
          if (parsed.type) {
            if (parsed.type === "bot") {
              setShowLoading(true);
              setLoadingMessage(parsed.content);
            } else if (parsed.type === "info_gather") {
              setShowLoading(false);
              setMsg(parsed.content);
            } else {
              setShowLoading(false);
              setMsg(prev => prev + parsed.content);
            }
          }
        } catch (e) {
          console.log(e)
          console.error("Invalid JSON:", str);
        }
      });
    }
  }, [content, setLoadingMessage, setShowLoading]);

  const markdownComponents = {
    // Ensure proper spacing for paragraphs
    p: ({ children }: any) => <p className="mb-4 last:mb-0">{children}</p>,
    
    // Style lists properly
    ul: ({ children }: any) => <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>,
    ol: ({ children }: any) => <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>,
    li: ({ children }: any) => <li className="ml-4">{children}</li>,
    
    // Style headings
    h1: ({ children }: any) => <h1 className="text-2xl font-bold mb-4">{children}</h1>,
    h2: ({ children }: any) => <h2 className="text-xl font-semibold mb-3">{children}</h2>,
    h3: ({ children }: any) => <h3 className="text-lg font-medium mb-2">{children}</h3>,
    
    // Style code blocks
    code: ({ inline, children }: any) => 
      inline ? (
        <code className="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm font-mono">
          {children}
        </code>
      ) : (
        <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto mb-4">
          <code className="text-sm font-mono">{children}</code>
        </pre>
      ),
    
    // Style blockquotes
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-gray-300 pl-4 italic mb-4">
        {children}
      </blockquote>
    ),
  };

  if (content?.role === "user") {
    return (
      <div className="w-[80%] ml-auto bg-gray-900/50 rounded-2xl p-4">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {content.message}
        </ReactMarkdown>
      </div>
    );
  } else if (content?.role === "assistant") {
    return (
      <div className="w-full p-4">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {msg}
        </ReactMarkdown>
      </div>
    );
  } else {
    return (
      <div className="w-full p-4">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {msg}
        </ReactMarkdown>
      </div>
    );
  }
};