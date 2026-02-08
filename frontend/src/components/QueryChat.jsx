import React, { useState, useRef, useEffect } from 'react';
import { Send, Copy, Download, FileText, Sheet } from 'lucide-react';
import { toast } from 'react-toastify';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import * as XLSX from 'xlsx';
import { apiClient } from '../api/client';

// Single clean QueryChat component
export const QueryChat = React.forwardRef((props, ref) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [queryType, setQueryType] = useState(null); // AI agent decides if null
  const messagesEndRef = useRef(null);

  // Expose method to add messages from external components
  React.useImperativeHandle(ref, () => ({
    addMessage: (content, actionType = null) => {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content,
        actionType,
      }]);
    },
  }));

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apiClient.ragQuery(input, queryType);
      console.log('RAG Response:', response.data);
      console.log('Detected action type:', response.data.type);
      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        sources: response.data.sources,
        actionType: response.data.type, // Capture the action type that was used
      };
      setMessages((prev) => [...prev, assistantMessage]);
      toast.success(`✓ ${response.data.type.charAt(0).toUpperCase() + response.data.type.slice(1).replace(/_/g, ' ')} action completed`);
    } catch (err) {
      console.error('Error:', err);
      setMessages((prev) => [...prev, { role: 'assistant', content: err?.response?.data?.error || 'Failed to get response', isError: true }]);
      toast.error('Query failed');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.info('Copied to clipboard');
  };

  const downloadAsText = (text, filename = 'nexqa_response.txt') => {
    const a = document.createElement('a');
    a.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(text || '');
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast.info('Downloaded as text');
  };

  const extractTablesFromContent = (content) => {
    const tables = [];
    const lns = (content || '').split('\n');
    let i = 0;
    while (i < lns.length) {
      if (lns[i].includes('|')) {
        const tbl = [];
        while (i < lns.length && lns[i].includes('|')) {
          tbl.push(lns[i]);
          i++;
        }
        if (tbl.length > 0) {
          tables.push(tbl);
        }
      } else {
        i++;
      }
    }
    return tables;
  };

  const downloadAsExcel = (content, filename = 'nexqa_response.xlsx') => {
    try {
      const tables = extractTablesFromContent(content);
      
      if (tables.length === 0) {
        toast.warning('No table data found in this response');
        return;
      }

      const wb = XLSX.utils.book_new();
      
      tables.forEach((tbl, tableIdx) => {
        const rows = tbl.map((l) => 
          l.split('|')
            .map((c) => c.trim())
            .filter((c, i2, arr) => !(i2 === 0 && c === '') && !(i2 === arr.length - 1 && c === ''))
        );
        
        if (rows.length > 0) {
          const header = rows[0] || [];
          const dataRows = rows.slice(1).filter((r) => r.length > 0);
          
          if (header.length > 0) {
            const wsData = [header, ...dataRows];
            const ws = XLSX.utils.aoa_to_sheet(wsData);
            
            // Auto-adjust column widths
            const colWidths = header.map((_, colIdx) => {
              const maxWidth = Math.max(
                header[colIdx]?.toString().length || 0,
                ...dataRows.map((row) => (row[colIdx]?.toString().length || 0))
              );
              return { wch: Math.min(maxWidth + 2, 50) };
            });
            ws['!cols'] = colWidths;
            
            const sheetName = tables.length > 1 ? `Table ${tableIdx + 1}` : 'Data';
            XLSX.utils.book_append_sheet(wb, ws, sheetName);
          }
        }
      });
      
      if (wb.SheetNames.length > 0) {
        XLSX.writeFile(wb, filename);
        toast.success(`✓ Downloaded as Excel with ${wb.SheetNames.length} table(s)`);
      } else {
        toast.warning('No valid tables found to export');
      }
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      toast.error('Failed to export as Excel');
    }
  };

  const hasTableContent = (content) => {
    return (content || '').includes('|');
  };

  const formatForMarkdown = (txt) => {
    if (!txt) return '';
    // Normalize line endings
    let s = String(txt).replace(/\r\n/g, '\n').replace(/\r/g, '\n');

    // Split into lines and convert obvious section headings (e.g. "Validation Analysis:")
    // into markdown headings so they render distinctly.
    const lines = s.split('\n');
    const transformed = lines.map((ln, idx) => {
      const t = ln.trim();
      if (!t) return '';
      // Heading pattern: starts with capital letter, few words, ends with ':'
      if (/^[A-Z][A-Za-z0-9\s\-\(\)\.,]{0,120}:$/.test(t)) {
        const heading = t.replace(/:$/, '');
        return `### ${heading}`;
      }
      // Also treat lines that are ALL CAPS words as headings
      if (/^[A-Z0-9\s\-]{3,120}$/.test(t) && t === t.toUpperCase() && t.length > 3) {
        return `### ${t}`;
      }
      return t;
    });

    s = transformed.join('\n');

    // Add line breaks before headings and numbered lists, but preserve existing blank lines
    s = s.split('\n').reduce((acc, line, idx, arr) => {
      if (!line.trim()) return acc + '\n';
      // Add spacing before headings if previous line has content
      if (line.trim().startsWith('###') && acc.trim() && !acc.endsWith('\n\n')) {
        return acc + '\n\n' + line;
      }
      // Add spacing before numbered lists if previous line has content
      if (/^\s*\d+\./.test(line) && acc.trim() && !acc.endsWith('\n\n')) {
        return acc + '\n\n' + line;
      }
      return acc + '\n' + line;
    }, '');

    return s;
  };

  function SourceSnippet({ content }) {
    const [expanded, setExpanded] = useState(false);
    const limit = 600;
    const raw = String(content || '');
    const displayed = !expanded && raw.length > limit ? raw.slice(0, limit) + '...' : raw;

    const blocks = [];
    const lines = displayed.split('\n');
    let i = 0;
    while (i < lines.length) {
      if (lines[i].includes('|')) {
        const tbl = [];
        while (i < lines.length && lines[i].includes('|')) { tbl.push(lines[i]); i++; }
        blocks.push({ type: 'table', lines: tbl });
      } else {
        const txt = [];
        while (i < lines.length && !lines[i].includes('|')) { txt.push(lines[i]); i++; }
        blocks.push({ type: 'text', text: txt.join('\n') });
      }
    }

    return (
      <div>
        {blocks.map((b, idx) => {
          if (b.type === 'text') {
            return (
              <div key={idx} className="mb-1">
                <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose prose-invert max-w-none text-xs leading-6 whitespace-pre-wrap">
                  {formatForMarkdown(b.text)}
                </ReactMarkdown>
              </div>
            );
          }

          const rows = b.lines.map((l) => l.split('|').map((c) => c.trim()).filter((c, i2, arr) => !(i2 === 0 && c === '') && !(i2 === arr.length - 1 && c === '')));
          const header = rows[0] || [];
          const body = rows.slice(1) || [];

          return (
            <div key={idx} className="overflow-x-auto my-2">
              <table className="min-w-full table-auto border-collapse text-xs">
                <thead>
                  <tr>{header.map((h, hi) => <th key={hi} className="px-2 py-1 text-left border-b border-white/10 bg-white/5">{h || ' '}</th>)}</tr>
                </thead>
                <tbody>
                  {body.map((r, ri) => (
                    <tr key={ri} className={ri % 2 === 0 ? 'bg-white/2' : ''}>
                      {header.map((_, ci) => <td key={ci} className="px-2 py-1 align-top text-gray-300 whitespace-normal break-words">{r[ci] || ''}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })}

        {raw.length > limit && (
          <button onClick={() => setExpanded((s) => !s)} className="mt-1 text-blue-300 text-xs hover:underline">
            {expanded ? 'Show less' : 'Show more'}
          </button>
        )}
      </div>
    );
  }

  const parseAndRender = (content) => {
    const parts = [];
    const lns = (content || '').split('\n');
    let j = 0;
    while (j < lns.length) {
      if (lns[j].includes('|')) {
        const t = [];
        while (j < lns.length && lns[j].includes('|')) { t.push(lns[j]); j++; }
        parts.push({ type: 'table', lines: t });
      } else {
        const t = [];
        while (j < lns.length && !lns[j].includes('|')) { t.push(lns[j]); j++; }
        parts.push({ type: 'text', text: t.join('\n') });
      }
    }

    return parts.map((p, idx) => {
      if (p.type === 'text') {
        return (
          <div key={idx} className="mb-1">
            <ReactMarkdown remarkPlugins={[remarkGfm]} className="prose prose-invert max-w-none text-sm leading-5 whitespace-pre-wrap">
              {formatForMarkdown(p.text)}
            </ReactMarkdown>
          </div>
        );
      }

      const rows = p.lines.map((l) => l.split('|').map((c) => c.trim()).filter((c, i2, arr) => !(i2 === 0 && c === '') && !(i2 === arr.length - 1 && c === '')));
      const header = rows.length > 0 ? rows[0] : [];
      const dataRows = rows.slice(1).filter((r) => r.length > 0);

      return (
        <div key={idx} className="overflow-x-auto my-2">
          <table className="min-w-full table-auto border-collapse text-sm">
            <thead>
              <tr>{header.map((h, hi) => <th key={hi} className="px-2 py-1 text-left border-b border-white/10 bg-white/5">{h || ' '}</th>)}</tr>
            </thead>
            <tbody>
              {dataRows.map((r, ri) => (
                <tr key={ri} className={ri % 2 === 0 ? 'bg-white/2' : ''}>
                  {header.map((_, ci) => <td key={ci} className="px-2 py-1 align-top text-gray-300 whitespace-normal break-words">{r[ci] || ''}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    });
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400 p-6">
            <div className="text-center max-w-2xl">
              <p className="text-3xl font-bold mb-4 text-white">Welcome to NexQA.ai</p>
              
              <div className="mb-6 p-4 rounded-lg bg-blue-500/10 border border-blue-400/30">
                <p className="text-lg mb-4 text-gray-300">Get started by uploading documents, then ask questions below!</p>
              </div>

              <div className="text-left space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-white mb-3">💡 Available Actions:</h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li><span className="font-medium text-blue-300">Ask Questions</span> - Get insights and answers from your documents</li>
                    <li><span className="font-medium text-purple-300">Summary</span> - Generate a concise summary of your documents</li>
                    <li><span className="font-medium text-yellow-300">Test Cases</span> - Create test cases from your documentation</li>
                    <li><span className="font-medium text-orange-300">Test Case Excel</span> - Export test cases in Excel format</li>
                    <li><span className="font-medium text-cyan-300">Test Strategy</span> - Develop a comprehensive test strategy</li>
                    <li><span className="font-medium text-red-300">Risk Analysis</span> - Identify potential risks and issues</li>
                    <li><span className="font-medium text-green-300">Validation</span> - Validate test cases and scenarios</li>
                    <li><span className="font-medium text-indigo-300">Automation</span> - Get automation recommendations and scripts</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-white mb-2">📝 How to use:</h3>
                  <ol className="space-y-1 text-sm text-gray-300 list-decimal list-inside">
                    <li>Upload your documents using the Document Upload feature</li>
                    <li>Type your question or request in the message box below</li>
                    <li>The AI will automatically detect the best action type for your query</li>
                    <li>View sources and export responses as needed</li>
                  </ol>
                </div>

                <div className="text-xs text-gray-400 mt-4 p-3 rounded bg-white/5">
                  ℹ️ Tip: The AI intelligently determines the action type based on your question. You can ask naturally and let it decide!
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div>
                {msg.role === 'assistant' && msg.actionType && !msg.isError && (
                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-xs font-semibold text-gray-400">Action:</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      msg.actionType === 'ask' ? 'bg-blue-500/30 text-blue-300 border border-blue-400/50' :
                      msg.actionType === 'summary' ? 'bg-purple-500/30 text-purple-300 border border-purple-400/50' :
                      msg.actionType === 'test_case' ? 'bg-yellow-500/30 text-yellow-300 border border-yellow-400/50' :
                      msg.actionType === 'testcase_excel' ? 'bg-orange-500/30 text-orange-300 border border-orange-400/50' :
                      msg.actionType === 'test_strategy' ? 'bg-cyan-500/30 text-cyan-300 border border-cyan-400/50' :
                      msg.actionType === 'risk' ? 'bg-red-500/30 text-red-300 border border-red-400/50' :
                      msg.actionType === 'validation' ? 'bg-green-500/30 text-green-300 border border-green-400/50' :
                      msg.actionType === 'automation' ? 'bg-indigo-500/30 text-indigo-300 border border-indigo-400/50' :
                      'bg-gray-500/30 text-gray-300 border border-gray-400/50'
                    }`}>
                      {msg.actionType.charAt(0).toUpperCase() + msg.actionType.slice(1).replace(/_/g, ' ')}
                    </span>
                  </div>
                )}
                {/* Responsive message bubble: user messages stay smaller, assistant messages fill available width */}
                <div className={
                  msg.role === 'user'
                    ? `glassmorphism rounded-2xl p-4 inline-block max-w-[85%] lg:max-w-[60%] ${msg.isError ? 'bg-red-500/20 border border-red-500/30' : 'bg-blue-500/30 border border-blue-400/50'}`
                    : `glassmorphism rounded-2xl p-4 w-full max-w-full ${msg.isError ? 'bg-red-500/20 border border-red-500/30' : 'bg-green-500/20 border border-green-400/50'}`
                }>
                  <div className="w-full">
                    {parseAndRender(msg.content || '')}
                  </div>
                </div>

                {msg.role === 'assistant' && !msg.isError && (
                  <div className="flex gap-2 mt-3 pt-3 border-t border-white/10">
                    <button onClick={() => copyToClipboard(msg.content)} className="p-2 hover:bg-white/10 rounded-lg transition-all" title="Copy">
                      <Copy className="w-4 h-4" />
                    </button>
                    <button onClick={() => downloadAsText(msg.content)} className="p-2 hover:bg-white/10 rounded-lg transition-all" title="Download as text">
                      <Download className="w-4 h-4" />
                    </button>
                    {hasTableContent(msg.content) && (
                      <button onClick={() => downloadAsExcel(msg.content)} className="p-2 hover:bg-green-500/20 rounded-lg transition-all" title="Download as Excel">
                        <Sheet className="w-4 h-4 text-green-400" />
                      </button>
                    )}
                  </div>
                )}

                {msg.role === 'assistant' && !msg.isError && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10 text-xs text-gray-300">
                    <div className="font-semibold mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Knowledge Sources
                    </div>
                    <div className="space-y-2">
                      {msg.sources.map((s, i) => (
                        <div key={i} className="p-2 bg-white/5 rounded-md">
                          <div className="text-xs text-gray-100 font-medium">{s.metadata?.file_name || s.metadata?.source || s.metadata?.url || 'Source'}</div>
                          <div className="text-xs text-gray-400"><SourceSnippet content={s.content} /></div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="glassmorphism rounded-2xl p-4">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask a question about your documents..." disabled={isLoading} className="flex-1 px-4 py-3 rounded-lg focus:outline-none bg-white/10" />
        <button type="submit" disabled={isLoading || !input.trim()} className="px-5 py-3 rounded-lg bg-blue-600 text-white disabled:opacity-50"><Send className="w-5 h-5" /></button>
      </form>
    </div>
  );
});

