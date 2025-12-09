import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BotIcon, UsersIcon } from './icons';
import ToolCallDisplay from './ToolCallDisplay';
import './ChatMessage.css';

export default function ChatMessage({ message, isUser, agentName = 'ACID' }) {
  const parseToolCalls = () => {
    if (!message.tool_call) return null;
    try {
      return JSON.parse(message.tool_call);
    } catch {
      return null;
    }
  };

  const toolCalls = parseToolCalls();
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes.toString().padStart(2, '0');
    return `${displayHours.toString().padStart(2, '0')}:${displayMinutes} ${ampm}`;
  };

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'ai-message'} ${isUser ? 'align-right' : 'align-left'}`}>
      <div className="message-avatar">
        {isUser ? <UsersIcon /> : <BotIcon />}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">{isUser ? 'You' : agentName}</span>
          <span className="message-time">{formatTime(message.created_at)}</span>
        </div>
        <div className="message-text">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
        {toolCalls && <ToolCallDisplay toolCalls={toolCalls} />}
      </div>
    </div>
  );
}
