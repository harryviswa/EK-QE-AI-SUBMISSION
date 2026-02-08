# Frontend Development Setup

This directory contains the React frontend for NexQA.ai with glassmorphism design.

## Features

- **Modern React 18** with Vite for fast development
- **Glassmorphism UI** - Frosted glass effect with Tailwind CSS
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Chat** - Interact with RAG system
- **Document Management** - Upload and manage knowledge sources
- **Export Features** - Copy, download, or export to PDF/Excel
- **Dark Theme** - Eye-friendly dark interface with animated background

## Directory Structure

```
src/
├── components/          # React components
│   ├── DocumentUpload.jsx    # File upload component
│   ├── QueryChat.jsx         # Chat interface
│   ├── SourceManager.jsx      # Document source management
│   ├── Sidebar.jsx           # Navigation sidebar
│   └── GlassBackground.jsx    # Animated background
├── api/                 # API utilities
│   └── client.js        # Axios API client
├── styles/              # Global styles
│   └── globals.css      # Glassmorphism styles
├── App.jsx              # Main App component
└── main.jsx             # React entry point
```

## Development

### Install dependencies
```bash
npm install
```

### Start development server
```bash
npm run dev
```

Server runs on http://localhost:3000

### Build for production
```bash
npm run build
```

Output in `dist/` directory

## Component Details

### DocumentUpload
- Drag & drop file upload
- Support for PDF, TXT, XLSX, XLS
- File size validation (50MB max)
- Loading states and error handling

### QueryChat
- Multiple query types (QA, Test Cases, Strategy, Risk, Validation)
- Markdown support for rich formatting
- Copy to clipboard and download features
- Real-time response streaming
- Message history with sources

### SourceManager
- List uploaded documents
- Add web pages via URL
- Remove knowledge sources
- Real-time document tracking

### GlassBackground
- Animated blob gradient background
- Grid overlay pattern
- Smooth animations
- Performance optimized

## Styling

The app uses **Tailwind CSS** with custom glassmorphism components:

```css
.glassmorphism {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

Customize in `tailwind.config.js` and `src/styles/globals.css`

## API Integration

The app communicates with the Flask backend at `/api` endpoints:

- Document upload and management
- RAG queries with multiple types
- Search and retrieval
- Export functions

See `src/api/client.js` for API client configuration.

## Environment Variables

Create `.env` file from `.env.example`:

```env
VITE_API_URL=http://localhost:5000/api
```

## Performance Tips

1. **Lazy load components** - Use React.lazy() for code splitting
2. **Optimize images** - Use WebP format where possible
3. **Cache API responses** - Implement React Query for better caching
4. **Monitor bundle size** - Use `npm run build` and check dist/

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires support for:
- CSS Backdrop Filter
- CSS Grid & Flexbox
- ES2020+ JavaScript features

---

For more information, see the [main README.md](../README.md)
