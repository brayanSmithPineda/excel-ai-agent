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
    
    // NEW: Code execution metadata
    executedCode?: boolean;
    codeOutput?: string;
    outputFiles?: Record<string, string>;
    executionReason?: string;
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

            // Build AI message with execution metadata
            const aiMessage: Message = {
                role: "ai",
                content: result.ai_response,
                timestamp: new Date(),
                executedCode: result.executed_code,
                codeOutput: result.code_output,
                outputFiles: result.output_files,
                executionReason: result.execution_reason
            };
            setMessages(prev => [...prev, aiMessage]);

            // Save conversation ID for continuity
            setConversationId(result.conversation_id);

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
                const newSheet = context.workbook.worksheets.add(filename.replace('.xlsx', ''));
                const range = newSheet.getRangeByIndexes(
                    0, 0, 
                    data.length, 
                    Math.max(...data.map((row: any[]) => row.length))
                );
                range.values = data;
                newSheet.activate();
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
                        
                        {/* Code execution indicator */}
                        {msg.executedCode && (
                            <div style={{ marginTop: '8px', padding: '4px 8px', backgroundColor: '#e3f2fd', borderRadius: '4px', fontSize: '12px' }}>
                                🔧 Code executed: {msg.executionReason}
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