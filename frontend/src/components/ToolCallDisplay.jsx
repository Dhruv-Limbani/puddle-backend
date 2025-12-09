import React from 'react';
import { DatabaseIcon, UsersIcon, CheckIcon, TagIcon } from './icons';
import './ToolCallDisplay.css';

export default function ToolCallDisplay({ toolCalls }) {
  if (!toolCalls || !toolCalls.calls || toolCalls.calls.length === 0) {
    return null;
  }

  const renderToolResult = (call) => {
    // Prioritize result_json if available, fallback to parsing result string
    let data = call.result_json;
    
    if (!data && call.result) {
      try {
        // Try to parse result as JSON
        const parsedResult = JSON.parse(call.result);
        data = parsedResult;
      } catch {
        // If not JSON, display as text
        return (
          <div className="tool-result-text">
            <pre>{call.result}</pre>
          </div>
        );
      }
    }

    // If still no data, show nothing
    if (!data) {
      return null;
    }

    // Handle different tool types
    switch (call.name) {
      case 'search_datasets':
      case 'get_buyer_datasets':
        return renderDatasets(data);
      
      case 'get_vendor_details':
        return renderVendor(data);
      
      case 'get_inquiry_full_state':
        return renderInquiry(data);
      
      case 'get_vendor_work_queue':
        return renderWorkQueue(data);
      
      default:
        // Generic JSON display
        return (
          <div className="tool-result-generic">
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        );
    }
  };

  const renderDatasets = (datasets) => {
    if (!Array.isArray(datasets) || datasets.length === 0) {
      return <div className="tool-empty">No datasets found</div>;
    }

    return (
      <div className="tool-datasets">
        <div className="tool-header">
          <DatabaseIcon />
          <span>{datasets.length} dataset{datasets.length !== 1 ? 's' : ''} found</span>
        </div>
        <div className="dataset-grid-tool">
          {datasets.slice(0, 3).map((dataset, idx) => (
            <div key={idx} className="dataset-card-tool">
              <h4>{dataset.title}</h4>
              <p className="dataset-desc">{dataset.description || 'No description'}</p>
              <div className="dataset-meta-tool">
                {dataset.domain && <span className="meta-badge">{dataset.domain}</span>}
                {dataset.pricing_model && <span className="meta-badge">{dataset.pricing_model}</span>}
              </div>
              {dataset.topics && dataset.topics.length > 0 && (
                <div className="dataset-topics">
                  {dataset.topics.slice(0, 3).map((topic, i) => (
                    <span key={i} className="topic-chip">{topic}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
        {datasets.length > 3 && (
          <div className="tool-more">+ {datasets.length - 3} more datasets</div>
        )}
      </div>
    );
  };

  const renderVendor = (vendor) => {
    return (
      <div className="tool-vendor">
        <div className="tool-header">
          <UsersIcon />
          <span>Vendor Details</span>
        </div>
        <div className="vendor-card-tool">
          <h4>{vendor.name}</h4>
          {vendor.description && <p>{vendor.description}</p>}
          <div className="vendor-meta-tool">
            {vendor.industry_focus && <span><TagIcon /> {vendor.industry_focus}</span>}
            {vendor.country && <span>📍 {vendor.country}</span>}
          </div>
          {vendor.contact_email && (
            <div className="vendor-contact">
              <span>📧 {vendor.contact_email}</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderInquiry = (inquiry) => {
    return (
      <div className="tool-inquiry">
        <div className="tool-header">
          <CheckIcon />
          <span>Inquiry #{inquiry.id}</span>
        </div>
        <div className="inquiry-card-tool">
          <div className="inquiry-status-badge badge-status-{inquiry.status}">
            {inquiry.status}
          </div>
          {inquiry.buyer_requirements && (
            <div className="inquiry-requirements">
              <strong>Requirements:</strong>
              <pre>{JSON.stringify(inquiry.buyer_requirements, null, 2)}</pre>
            </div>
          )}
          {inquiry.vendor_response && (
            <div className="inquiry-response">
              <strong>Vendor Response:</strong>
              <pre>{JSON.stringify(inquiry.vendor_response, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderWorkQueue = (workQueue) => {
    if (!Array.isArray(workQueue) || workQueue.length === 0) {
      return <div className="tool-empty">No pending inquiries</div>;
    }

    return (
      <div className="tool-work-queue">
        <div className="tool-header">
          <CheckIcon />
          <span>{workQueue.length} inquiry item{workQueue.length !== 1 ? 's' : ''}</span>
        </div>
        <div className="work-queue-list">
          {workQueue.map((item, idx) => (
            <div key={idx} className="work-queue-item">
              <div className="work-item-header">
                <span className="work-item-id">Inquiry #{item.id}</span>
                <span className={`badge-status badge-status-${item.status}`}>{item.status}</span>
              </div>
              {item.buyer_name && <div className="work-item-buyer">From: {item.buyer_name}</div>}
              {item.dataset_title && <div className="work-item-dataset">Dataset: {item.dataset_title}</div>}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="tool-calls-container">
      {toolCalls.calls.map((call, idx) => (
        <div key={idx} className="tool-call-item">
          <div className="tool-call-label">
            🔧 {call.name}
          </div>
          {renderToolResult(call)}
        </div>
      ))}
    </div>
  );
}
