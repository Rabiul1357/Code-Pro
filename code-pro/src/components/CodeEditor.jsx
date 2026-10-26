import React, { useState } from "react";
import Editor from "@monaco-editor/react";
import { Copy, Check, RotateCcw, Code, Lock, Unlock } from "lucide-react";

export default function CodeEditor({ code, language, onChange, onReset }) {
  const [copied, setCopied] = useState(false);
  const [currentLang, setCurrentLang] = useState(language || "cpp");
  const [isReadOnly, setIsReadOnly] = useState(true); // Read-only by default to prevent mobile keyboard popups

  // Keep internal language synced when question changes
  React.useEffect(() => {
    if (language) {
      setCurrentLang(language.toLowerCase());
    }
  }, [language]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Clipboard copy failed:", err);
    }
  };

  // Map common language names to Monaco supported identifiers
  const getMonacoLang = (lang) => {
    const l = (lang || "").toLowerCase();
    if (l === "c++" || l === "cpp") return "cpp";
    if (l === "py" || l === "python") return "python";
    if (l === "js" || l === "javascript") return "javascript";
    if (l === "ts" || l === "typescript") return "typescript";
    if (l === "cs" || l === "csharp") return "csharp";
    if (l === "java") return "java";
    if (l === "go") return "go";
    if (l === "rust") return "rust";
    return "cpp";
  };

  return (
    <div className="editor-wrapper">
      <div className="editor-toolbar">
        <div className="editor-toolbar-left">
          <Code size={16} color="#6366f1" />
          <select
            className="select-input"
            value={currentLang}
            onChange={(e) => setCurrentLang(e.target.value)}
          >
            <option value="cpp">C++</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="csharp">C#</option>
            <option value="go">Go</option>
          </select>

          {/* Read-Only Status & Toggle */}
          <button
            onClick={() => setIsReadOnly(!isReadOnly)}
            className="btn btn-secondary btn-sm"
            style={{ fontSize: "0.75rem", padding: "0.25rem 0.5rem" }}
            title={isReadOnly ? "Editor is Read-Only (Safe for mobile). Click to allow typing." : "Click to lock editor as Read-Only"}
          >
            {isReadOnly ? (
              <>
                <Lock size={12} color="#10b981" /> <span className="btn-label-desktop">Read Only</span>
              </>
            ) : (
              <>
                <Unlock size={12} color="#f59e0b" /> <span className="btn-label-desktop">Editing</span>
              </>
            )}
          </button>
        </div>

        <div className="editor-toolbar-right">
          {onReset && (
            <button
              onClick={onReset}
              className="btn btn-secondary btn-sm"
              title="Reset to Original Bot Solution"
            >
              <RotateCcw size={13} /> Reset
            </button>
          )}

          <button
            onClick={handleCopy}
            className={`btn ${copied ? "btn-success" : "btn-primary"} btn-sm`}
            title="Copy entire code to clipboard"
          >
            {copied ? (
              <>
                <Check size={14} /> Copied!
              </>
            ) : (
              <>
                <Copy size={14} /> Copy Code
              </>
            )}
          </button>
        </div>
      </div>

      <div className="editor-container">
        <Editor
          height="100%"
          language={getMonacoLang(currentLang)}
          value={code || "// No code available"}
          theme="vs-dark"
          onChange={isReadOnly ? undefined : onChange}
          options={{
            readOnly: isReadOnly,
            domReadOnly: isReadOnly, // Prevents mobile soft keyboard from opening on tap
            fontSize: 14,
            fontFamily: "'Fira Code', Consolas, 'Courier New', monospace",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            lineNumbers: "on",
            renderLineHighlight: "all",
            smoothScrolling: true,
            padding: { top: 12, bottom: 12 }
          }}
        />
      </div>
    </div>
  );
}
