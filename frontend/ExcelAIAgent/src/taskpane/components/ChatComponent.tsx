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

import * as React from "react";
import { useState } from "react";
import {
    Button,
    Input,
    Card,
    CardHeader,
    Text,
    makeStyles,
    tokens
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
}

interface ChatResponse {
    ai_response: string;
    conversation_id: string;
    search_results?: {
        semantic_matches: number;
        excel_functions: number;
        workbook_symbols: number;
    };
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

            // Add AI response to UI
            const aiMessage: Message = {
                role: "ai",
                content: result.ai_response,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMessage]);

            // Save conversation ID for continuity
            setConversationId(result.conversation_id);

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
                    </div>
                ))}
                {isLoading && (
                    <div className={`${styles.message} ${styles.aiMessage}`}>
                        <Text>Thinking...</Text>
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
        </div>
    );
};

export default ChatComponent;