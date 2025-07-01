"use client"

import { ChatArea } from "@/components/ChatArea";
import { SideBar } from "@/components/SideBar";
import { useEffect } from "react";


export default function Home() {
  return (
    <div className="flex h-screen text-white">
      <SideBar />
      <ChatArea />
    </div>
  )
}