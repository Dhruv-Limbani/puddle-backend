import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BotIcon, UsersIcon } from './Icons';
import ToolCallDisplay from './ToolCallDisplay';
import './TideChatMessage.css';

export default function TideChatMessage({ message, isUser }) {

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
    <div className={`tide-chat-message ${isUser ? 'tide-user-message' : 'tide-ai-message'} ${isUser ? 'tide-align-right' : 'tide-align-left'}`}>
      <div className="tide-message-avatar">
        {isUser ? <UsersIcon /> : <BotIcon />}
      </div>
      <div className="tide-message-content">
        <div className="tide-message-header">
          <span className="tide-message-sender">{isUser ? 'You' : 'TIDE'}</span>
          <span className="tide-message-time">{formatTime(message.created_at)}</span>
        </div>
        <div className="tide-message-text">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
        {toolCalls && <ToolCallDisplay toolCalls={toolCalls} />}
      </div>
    </div>
  );
}
