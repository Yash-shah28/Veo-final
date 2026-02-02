import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Gradient Effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[100px] pointer-events-none" />

      <div className="z-10 max-w-2xl w-full text-center space-y-12 backdrop-blur-3xl p-8 rounded-3xl border border-white/10 bg-white/5 shadow-2xl">
        <div className="flex justify-center gap-8">
          <a href="https://vite.dev" target="_blank" className="hover:scale-110 transition-transform duration-300">
            <img src={viteLogo} className="w-24 h-24 drop-shadow-[0_0_15px_rgba(100,108,255,0.5)]" alt="Vite logo" />
          </a>
          <a href="https://react.dev" target="_blank" className="hover:scale-110 transition-transform duration-300">
            <img src={reactLogo} className="w-24 h-24 animate-[spin_20s_linear_infinite] drop-shadow-[0_0_15px_rgba(97,218,251,0.5)]" alt="React logo" />
          </a>
        </div>
        
        <div className="space-y-4">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Vite + React
          </h1>
          <p className="text-neutral-400 text-lg">
            Reimagined with Tailwind CSS v4
          </p>
        </div>

        <div className="flex flex-col items-center gap-6">
          <button 
            onClick={() => setCount((count) => count + 1)}
            className="px-8 py-3 bg-neutral-900 border border-neutral-700 hover:border-blue-500 rounded-xl font-semibold transition-all duration-300 shadow-[0_4px_14px_0_rgba(0,0,0,0.39)] hover:shadow-[0_6px_20px_rgba(93,93,255,0.23)] hover:-translate-y-1 active:scale-95 cursor-pointer"
          >
            Count is {count}
          </button>
          
          <p className="text-neutral-500 text-sm">
            Edit <code className="bg-neutral-900 px-2 py-1 rounded text-neutral-300 font-mono">src/App.jsx</code> and save to test HMR
          </p>
        </div>
      </div>

      <p className="absolute bottom-8 text-neutral-600">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  )
}

export default App
