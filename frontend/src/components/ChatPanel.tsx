import React from 'react';
import { Bot, Send, Mic, Languages, Sparkles } from 'lucide-react';

export const ChatPanel: React.FC = () => {
  return (
    <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5 shadow-sm space-y-4 h-full flex flex-col">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-cyan-950 border border-cyan-500/30 rounded-lg text-cyan-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">WeatherGPT AI Assistant</h3>
            <p className="text-[11px] text-slate-400">Conversational Risk & Weather Intelligence</p>
          </div>
        </div>
        <div className="flex items-center space-x-1.5">
          <button className="px-2 py-1 bg-slate-800 text-slate-300 rounded border border-slate-700/60 text-[11px] flex items-center space-x-1" disabled>
            <Languages className="w-3 h-3 text-cyan-400" />
            <span>Multilingual</span>
          </button>
        </div>
      </div>

      {/* Messages Feed Container Placeholder */}
      <div className="flex-1 min-h-[260px] bg-slate-950 p-4 rounded-lg border border-slate-800/80 overflow-y-auto space-y-3">
        {/* System Greeting */}
        <div className="flex items-start space-x-3">
          <div className="p-1.5 bg-cyan-950 border border-cyan-700/50 rounded-lg text-cyan-400 shrink-0">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="bg-slate-900 border border-slate-800 p-3 rounded-2xl rounded-tl-none text-xs text-slate-300 space-y-1 max-w-[85%]">
            <p className="font-semibold text-cyan-400">WeatherGPT Core Agent</p>
            <p>
              Welcome to WeatherGPT. I am ready to process weather queries, compute impact assessments, perform RAG over disaster protocols, and generate explainable AI risk insights.
            </p>
            <p className="text-[10px] text-slate-500 italic pt-1">
              LLM & RAG architecture hooks ready in backend/app/services/llm and backend/app/services/rag.
            </p>
          </div>
        </div>
      </div>

      {/* Input Prompt Box Placeholder */}
      <div className="relative flex items-center gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Ask WeatherGPT: 'What is the flood impact risk for Chennai tomorrow?'"
            className="w-full bg-slate-950 border border-slate-700/80 rounded-lg pl-4 pr-10 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
            disabled
          />
          <button className="absolute right-2.5 top-1/2 transform -translate-y-1/2 p-1 text-slate-400 hover:text-cyan-400 transition" disabled>
            <Mic className="w-4 h-4" />
          </button>
        </div>
        <button className="p-2.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 rounded-lg font-medium transition shrink-0 opacity-80 cursor-not-allowed" disabled>
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
