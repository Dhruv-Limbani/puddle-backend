import React from 'react';
import { BotIcon, UsersIcon } from './icons';
import ToolCallDisplay from './ToolCallDisplay';
import './ChatMessage.css';

export default function ChatMessage({ message, isUser }) {
  const renderMarkdown = (text) => {
    if (!text) return '';
    let html = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^\s*\-\s+(.*)$/gm, '<li>$1</li>')
      .replace(/\n/g, '<br/>');
    // Wrap list items in <ul>
    html = html.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
    return html;
  };
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
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'ai-message'} ${isUser ? 'align-right' : 'align-left'}`}>
      <div className="message-avatar">
        {isUser ? <UsersIcon /> : <BotIcon />}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">{isUser ? 'You' : 'ACID'}</span>
          <span className="message-time">{formatTime(message.created_at)}</span>
        </div>
        <div className="message-text" dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }} />
        {toolCalls && <ToolCallDisplay toolCalls={toolCalls} />}
      </div>
    </div>
  );
}
