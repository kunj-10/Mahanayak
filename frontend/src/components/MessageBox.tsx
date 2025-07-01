"use client"

import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

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
    console.log(content)
    if (typeof content?.message === 'string') {
      const rawMatches = content.message.match(/{[^]*?}/g) || [];
      setMsg("");
      const parsedMatches = rawMatches.map((str) => {
        try {
          let parsed = JSON.parse(str);
          if (parsed.type) {
            if (parsed.type === "bot") {
              setShowLoading(true);
              setLoadingMessage(parsed.content)
            } else if (parsed.type === "info_gather") {
              setShowLoading(false);
              setMsg(parsed.content);
            }
            else  {
              setShowLoading(false);
              setMsg(prev => prev + parsed.content);
            }
          }
          return parsed;
        } catch (e) {
          console.error("Invalid JSON:", str);
          return null;
        }
      }).filter(Boolean);

    }
  }, [content]);


  if (content?.role === "user") {
    return (
      <div className="w-[80%] ml-auto bg-gray-900/50 rounded-2xl p-4">
        <ReactMarkdown>
          {content.message}
        </ReactMarkdown>
      </div>
    )
  } else if (content?.role === "assistant") {
    return (
      <>
        <div className="w-full p-4">
          <ReactMarkdown>
            {msg}
          </ReactMarkdown>
        </div>
      </>

    );
  } else {
    return (
      <div className="w-full p-4">
        <ReactMarkdown>
          {msg}
        </ReactMarkdown>
      </div>
    );

  }

};