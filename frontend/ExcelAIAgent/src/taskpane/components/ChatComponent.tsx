/**
 * Chat Component - Intelligent Conversational UI
 * 
 * This component provides a conversational interface that leverages:
 * - Semantic search (past conversations)
 * - Excel function knowledge base
 * - Hybrid search (workbook symbols)
 * 
 * Separate from AIExecutor which focuses on code execution
 */

import { sendChatMessage } from '../services/apiService'
import * as XLSX from 'xlsx';

import * as React from "react";
import { useState } from "react";
import {
    Button,
    Input,
    Card,
    CardHeader,
    Text,
    makeStyles,
    tokens,
    Spinner
} from "@fluentui/react-components";
import { Send24Regular } from "@fluentui/react-icons";

// ===========================================
// STYLES
// ===========================================

const useStyles = makeStyles({
    container: {
        display: "flex",
        flexDirection: "column",
        height: "100%",
        padding: "16px"
    },
    messagesContainer: {
        flex: 1,
        overflowY: "auto",
        marginBottom: "16px",
        display: "flex",
        flexDirection: "column",
        gap: "12px"
    },
    message: {
        padding: "12px",
        borderRadius: "8px",
        maxWidth: "80%"
    },
    userMessage: {
        alignSelf: "flex-end",
        backgroundColor: tokens.colorBrandBackground,
        color: tokens.colorNeutralForegroundOnBrand
    },
    aiMessage: {
        alignSelf: "flex-start",
        backgroundColor: tokens.colorNeutralBackground3
    },
    inputContainer: {
        display: "flex",
        gap: "8px"
    }
});

// ===========================================
// TYPES
// Types are basically a interface that defines the shape of the data that we are going to use in the component
// Are the same as the backend Pydantic schemas
// ===========================================

interface Message {
    role: "user" | "ai";
    content: string;
    timestamp: Date;
    
    // Code execution metadata
    executedCode?: boolean;
    codeOutput?: string;
    outputFiles?: Record<string, string>;
    executionReason?: string;
    
    // NEW: Formula writing metadata
    wroteFormulas?: boolean;
    formulaReason?: string;
    targetColumn?: string;
}


// ===========================================
// COMPONENT
// ===========================================

const ChatComponent: React.FC = () => {
    const styles = useStyles();

    // State
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>("");
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [statusMessage, setStatusMessage] = useState<{type: string, text: string} | null>(null);

    // Send message handler
    const handleSendMessage = async () => {
        if (!input.trim()) return;

        // Add user message to UI
        const userMessage: Message = {
            role: "user",
            content: input,
            timestamp: new Date()
        };
        setMessages([...messages, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            // Call chat API using the new service
            const result = await sendChatMessage(input, conversationId);

            // DEBUG: Log full API response for testing
            console.log('🔍 DEBUG - Full API Response:', result);
            console.log('🔍 DEBUG - executed_code:', result.executed_code);
            console.log('🔍 DEBUG - execution_reason:', result.execution_reason);
            console.log('🔍 DEBUG - code_output:', result.code_output);
            console.log('🔍 DEBUG - output_files:', result.output_files);
            console.log('🔍 DEBUG - write_formulas:', result.write_formulas);

            // Build AI message with execution metadata
            const aiMessage: Message = {
                role: "ai",
                content: result.ai_response,
                timestamp: new Date(),
                executedCode: result.executed_code,
                codeOutput: result.code_output,
                outputFiles: result.output_files,
                executionReason: result.execution_reason,
                // NEW: Formula writing metadata
                wroteFormulas: result.write_formulas,
                formulaReason: result.formula_reason,
                targetColumn: result.target_column
            };
            setMessages(prev => [...prev, aiMessage]);

            // Save conversation ID for continuity
            setConversationId(result.conversation_id);

            // NEW: Auto-execute formulas if AI generated them
            if (result.write_formulas && result.office_js_code) {
                await handleExecuteFormulas(
                    result.office_js_code, 
                    result.formula_reason || "Adding formulas"
                );
            }

            // Show success message if code executed
            if (result.executed_code) {
                setStatusMessage({
                    type: "success",
                    text: `✅ ${result.execution_reason}`
                });
            }

        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage: Message = {
                role: "ai",
                content: "Sorry, I encountered an error. Please try again.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    // NEW: Formula execution handler (Office.js direct)
    const handleExecuteFormulas = async (officeJsCode: string, reason: string) => {
        setStatusMessage({ type: "info", text: `Writing formulas: ${reason}...` });
        
        try {
            // Execute the Office.js code directly
            // Create a function from the string and execute it
            const codeFunction = new Function('Excel', 'context', `return (async () => { ${officeJsCode} })();`);
            await codeFunction(Excel, null);
            
            setStatusMessage({ 
                type: "success", 
                text: `✅ Formulas added successfully!` 
            });
        } catch (error) {
            console.error("Formula execution error:", error);
            setStatusMessage({ 
                type: "error", 
                text: `Failed to write formulas: ${error.message}` 
            });
        }
    };

    // Excel insertion handler
    const handleInsertToExcel = async (filename: string, base64Content: string) => {
        setStatusMessage({ type: "info", text: `Inserting ${filename}...` });
        
        try {
            // Decode base64
            const binaryString = atob(base64Content);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            // Parse Excel file
            const workbook = XLSX.read(bytes, { type: "array" });
            const sheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[sheetName];
            const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][];
            
            // Insert into Excel using Office.js
            await Excel.run(async (context) => {
                // Get the currently active worksheet (context-aware)
                const activeWorksheet = context.workbook.worksheets.getActiveWorksheet();
                activeWorksheet.load("name");
                await context.sync();
                const activeTabName = activeWorksheet.name;
                
                // Use the active tab as the target sheet
                let targetSheet;
                try {
                    targetSheet = context.workbook.worksheets.getItem(activeTabName);
                } catch (error) {
                    // If the active sheet doesn't exist (shouldn't happen), create it
                    targetSheet = context.workbook.worksheets.add(activeTabName);
                }
                
                // Validate and clean data
                const cleanData = data.filter(row => row && row.length > 0);
                if (cleanData.length === 0) {
                    throw new Error("No valid data found in the file");
                }
                
                // Calculate dimensions safely
                const rowCount = cleanData.length;
                const columnCounts = cleanData.map(row => row ? row.length : 0);
                const maxColumnCount = Math.max(...columnCounts);
                
                console.log(`Inserting data: ${rowCount} rows, ${maxColumnCount} columns`);
                console.log('Sample data:', cleanData.slice(0, 3));
                
                // Normalize data to ensure all rows have the same number of columns
                const normalizedData = cleanData.map(row => {
                    const normalizedRow = new Array(maxColumnCount).fill('');
                    if (row) {
                        for (let i = 0; i < Math.min(row.length, maxColumnCount); i++) {
                            normalizedRow[i] = row[i] || '';
                        }
                    }
                    return normalizedRow;
                });
                
                // Clear existing data and insert new data
                const range = targetSheet.getRangeByIndexes(0, 0, rowCount, maxColumnCount);
                range.values = normalizedData;
                targetSheet.activate();
                await context.sync();
            });
            
            setStatusMessage({ 
                type: "success", 
                text: `✅ ${filename} inserted successfully!` 
            });
        } catch (error) {
            setStatusMessage({ 
                type: "error", 
                text: `Failed to insert ${filename}: ${error.message}` 
            });
        }
    };

    // TODO: Implement proper auth token retrieval
    const getAuthToken = () => {
        return "test-token-for-development";
    };

    return (
        <div className={styles.container}>
            <Card>
                <CardHeader
                    header={<Text weight="semibold">Intelligent Chat Assistant</Text>}
                    description={<Text size={200}>Ask questions about Excel, your data, or past conversations</Text>}
                />
            </Card>

            {/* Messages Display */}
            <div className={styles.messagesContainer}>
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`${styles.message} ${
                            msg.role === "user" ? styles.userMessage : styles.aiMessage
                        }`}
                    >
                        <Text>{msg.content}</Text>
                        
                        {/* DEBUG: Show all response fields for testing */}
                        {msg.role === "ai" && (
                            <div style={{ 
                                marginTop: '8px', 
                                padding: '8px', 
                                backgroundColor: '#f8f9fa', 
                                borderRadius: '4px', 
                                fontSize: '11px',
                                border: '1px solid #dee2e6',
                                fontFamily: 'monospace'
                            }}>
                                <div><strong>DEBUG - Response Fields:</strong></div>
                                <div>• executed_code: {msg.executedCode ? 'TRUE' : 'FALSE'}</div>
                                <div>• execution_reason: {msg.executionReason || 'null'}</div>
                                <div>• code_output: {msg.codeOutput ? 'Present' : 'null'}</div>
                                <div>• output_files: {msg.outputFiles && Object.keys(msg.outputFiles).length > 0 ? `${Object.keys(msg.outputFiles).length} files` : 'null'}</div>
                            </div>
                        )}
                        
                        {/* DEBUG: Show executed_code field for testing */}
                        <div style={{ 
                            marginTop: '8px', 
                            padding: '4px 8px', 
                            backgroundColor: msg.executedCode ? '#e8f5e8' : '#fff3cd', 
                            borderRadius: '4px', 
                            fontSize: '12px',
                            border: '1px solid #ddd'
                        }}>
                            <strong>DEBUG - executed_code:</strong> {msg.executedCode ? 'TRUE' : 'FALSE'}
                            {msg.executedCode && msg.executionReason && (
                                <div style={{ marginTop: '4px' }}>
                                    <strong>Reason:</strong> {msg.executionReason}
                                </div>
                            )}
                        </div>
                        
                        {/* Code execution indicator */}
                        {msg.executedCode && (
                            <div style={{ marginTop: '8px', padding: '4px 8px', backgroundColor: '#e3f2fd', borderRadius: '4px', fontSize: '12px' }}>
                                🔧 Code executed: {msg.executionReason}
                            </div>
                        )}
                        
                        {/* NEW: Formula writing indicator */}
                        {msg.wroteFormulas && (
                            <div style={{ marginTop: '8px', padding: '4px 8px', backgroundColor: '#d4edda', borderRadius: '4px', fontSize: '12px' }}>
                                📝 Formulas written: {msg.formulaReason}
                                {msg.targetColumn && ` (Column: ${msg.targetColumn})`}
                            </div>
                        )}
                        
                        {/* Code output display */}
                        {msg.codeOutput && (
                            <div style={{ marginTop: '8px' }}>
                                <Text weight="semibold" size={200}>Output:</Text>
                                <pre style={{ 
                                    backgroundColor: '#f5f5f5', 
                                    padding: '8px', 
                                    borderRadius: '4px', 
                                    fontSize: '12px',
                                    overflow: 'auto',
                                    maxHeight: '200px'
                                }}>
                                    {msg.codeOutput}
                                </pre>
                            </div>
                        )}
                        
                        {/* Generated files */}
                        {msg.outputFiles && Object.keys(msg.outputFiles).length > 0 && (
                            <div style={{ marginTop: '8px' }}>
                                <Text weight="semibold" size={200}>Generated Files:</Text>
                                {Object.entries(msg.outputFiles).map(([filename, base64]) => (
                                    <Button
                                        key={filename}
                                        appearance="primary"
                                        size="small"
                                        onClick={() => handleInsertToExcel(filename, base64)}
                                        style={{ marginTop: '4px', marginRight: '4px' }}
                                    >
                                        📊 Insert {filename} into Excel
                                    </Button>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
                {isLoading && (
                    <div className={`${styles.message} ${styles.aiMessage}`}>
                        <Spinner size="small" />
                        <Text style={{ marginLeft: '8px' }}>
                            {messages.length > 0 && messages[messages.length - 1].role === "user" 
                                ? "AI is thinking..." 
                                : "Executing code..."}
                        </Text>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className={styles.inputContainer}>
                <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask me anything..."
                    onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    style={{ flex: 1 }}
                />
                <Button
                    appearance="primary"
                    icon={<Send24Regular />}
                    onClick={handleSendMessage}
                    disabled={isLoading || !input.trim()}
                >
                    Send
                </Button>
            </div>

            {/* Status Message */}
            {statusMessage && (
                <div style={{
                    marginTop: '8px',
                    padding: '8px',
                    borderRadius: '4px',
                    backgroundColor: statusMessage.type === 'success' ? '#e8f5e8' : 
                                   statusMessage.type === 'error' ? '#ffeaea' : '#e3f2fd',
                    color: statusMessage.type === 'success' ? '#2e7d32' : 
                           statusMessage.type === 'error' ? '#d32f2f' : '#1976d2',
                    fontSize: '12px'
                }}>
                    {statusMessage.text}
                </div>
            )}
        </div>
    );
};

export default ChatComponent;