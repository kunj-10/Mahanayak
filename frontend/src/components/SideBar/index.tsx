'use client'

import React, { useState } from 'react'
import { FaPlus } from 'react-icons/fa'
import { FiSidebar } from 'react-icons/fi'

export const SideBar = () => {
  const [isSideBarOpen, setIsSideBarOpen] = useState<boolean>(true)

  return (
    <div
      className={`flex h-screen mr-2 transition-all duration-300 ${
        isSideBarOpen ? 'w-[18%]' : 'w-[50px]'
      } bg-gray-900 text-white`}
    >
      <div className='w-full mr-2'>

        <div className='h-fit flex flex-col items-end gap-2 p-2'>
          
          <div
            onClick={() => setIsSideBarOpen(prev => !prev)}
            className='h-[30px] w-[30px] flex items-center justify-center cursor-pointer hover:bg-gray-800 rounded'
          >
            <FiSidebar className='h-full w-full' />
          </div>

          
          <div
            className='flex items-center justify-start gap-1 h-fit w-full cursor-pointer hover:bg-gray-800 p-2 rounded'
            onClick={() => setIsSideBarOpen(prev => !prev)}
          >
            <div
              className={`${
                !isSideBarOpen && 'm-auto'
              } h-[20px] w-[20px] flex items-center justify-center`}
            >
              <FaPlus className='h-full w-full' />
            </div>
            {isSideBarOpen && <div className="text-gray-200">New Chat</div>}
          </div>
        </div>

        
        {isSideBarOpen && (
          <div className='p-4 text-sm text-gray-300'>
            Sidebar Content Here
           
          </div>
        )}
      </div>
    </div>
  )
}
