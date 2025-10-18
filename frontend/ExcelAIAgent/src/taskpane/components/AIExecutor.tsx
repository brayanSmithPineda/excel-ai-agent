//React imports -- useState for managing component state.
import * as React from "react";
import { useState } from "react";
import * as XLSX from "xlsx";

// Fluent UI components - Microsoft's design system components for add-ins
import {
    Button,
    Input,
    Textarea,
    Card,
    CardHeader,
    Text,
    makeStyles,
    tokens
} from "@fluentui/react-components";

// Fluent UI icons - Microsoft's design system icons for add-ins
import {
    ArrowUpload24Regular, //Upload icon
    Play24Regular, //Play icon for execution button
    Dismiss24Regular, //X icon for clearing input
} from "@fluentui/react-icons";

//Import our API service for making backend calls
import { executeTask, AIExecutorResponse, ExecutionErrorResponse } from "../services/apiService";

//===========================================
// COMPONENT STYLES - Using Fluent UI's makeStyles for consistent styling
//===========================================

const useStyles = makeStyles({
    container: {
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        marginTop: "20px",
        padding: "16px"
    },
    fileInput: {
        display: "none",
    },
    fileList: {
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        marginTop: "8px",
    },
    fileItem: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "8px",
        backgroundColor: tokens.colorNeutralBackground3,
        borderRadius: "4px",
    },
    resultsCard: {
        marginTop: "16px",
        padding: "16px",
    },
    codePreview: {
        backgroundColor: tokens.colorNeutralBackground3,
        padding: "12px",
        borderRadius: "4px",
        fontFamily: "monospace",
        fontSize: "12px",
        whiteSpace: "pre-wrap",
        maxHeight: "300px",
        overflowY: "auto",
    }
});

//===========================================
// COMPONENT - AI Executor
//===========================================

const AIExecutor: React.FC = () => {
    const styles = useStyles();
    //===========================================
    // STATE MANAGEMENT - useState hooks to track component state
    //===========================================

    //User's request text (example "stack these workbooks")
    const [userRequest, setUserRequest] = useState<string>("");

    // Array of uploaded files
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

    //Loading state - true when API call is in progress
    const [isLoading, setIsLoading] = useState<boolean>(false);

    //API response date (results, errors, or permission requests)
    const [response, setResponse] = useState<AIExecutorResponse | null>(null);

    //Status message state 
    const [statusMessage, setStatusMessage] = useState<{
        type: 'success' | 'error' | 'info';
        text: string;
    } | null>(null);

    //===========================================
    // EVENT HANDLERS - Functions that responds to user actions
    //===========================================

    /**
     * Handle file selection from file input
     * Why: User clicks "Upload Files" button -> we need to store the files in the state
     */
    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (files) {
            //convert first to FileList to array for easier manipulation
            const fileArray = Array.from(files);
            setSelectedFiles(fileArray);
        }
    };

    /**
     * Handle file removal from the list
     * Why: User clicks "X" button -> we need to remove the file from the state
     */
    const handleFileRemove = (file: File) => {
        setSelectedFiles(selectedFiles.filter((f) => f !== file));
    };

    /**
     * Execute the AI task by calling our backend API
     * Why: when the user clicks "Execute Task" button, we need to call the backend API
     */
    const handleExecuteTask = async () => {
        // Validation - ensure user entered a request
        if (!userRequest.trim()) {
            alert("Please enter a request");
            return;
        }   

        // Start loading state
        setIsLoading(true);
        setResponse(null); // clear previous response

        try {
            //Call our API services (from the apiService.ts file)
            const result = await executeTask({
                userRequest: userRequest,
                //if no files are selected, pass undefined instead of an empty array, the backend expects undefined if no files are provided
                files: selectedFiles.length > 0 ? selectedFiles : undefined,
            });

            //Store the response to display to user
            setResponse(result);
        } catch (error) {
            console.error("Error executing task:", error);
            setResponse({
                success: false,
                error: "An unexpected error occurred",
                details: error instanceof Error ? error.message : String(error)
            });
        } finally {
            //Always reset loading state
            setIsLoading(false);
        }
    };

    /**
     * Handle file download/opening
     *
     * IMPORTANT: Office WebView blocks programmatic downloads for security.
     * We offer two options:
     * 1. Open the file in a new browser window (user can then save it)
     * 2. (Future enhancement) Insert data directly into current workbook using Office.js
     */
    const handleDownloadFile = (filename: string, base64Data: string) => {
        try {
            // Step 1: Conver base64 the backend returns to binary data
            const binaryString = atob(base64Data);

            // Step 2: Convert to Uint8Array for XLSX.read
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            console.log("Byte array created, length:", bytes.length);

            // Step 3: Parse excel file using XLSX
            const workbook = XLSX.read(bytes, { type: "array" });

            // Step 4: Get the first sheet, this is the one we will insert the data into
            const firstSheet = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheet];
            /// Step 5: Convert worksheet to 2D array (rows and columns)
            // Why? Office.js Excel API expects data as a 2D array
            const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            console.log("Data extracted, rows:", data.length);
  
            // Step 6: Use Office.js to insert into Excel
            // Why? This is the proper way to modify Excel from an add-in
            Excel.run(async (context) => {
                // Create a new worksheet with the generated filename
                const sheets = context.workbook.worksheets;
                const newSheet = sheets.add(filename.replace('.xlsx', ''));
  
                // Get the range where we'll insert data
                // Why? We need to specify which cells to write to
                const range = newSheet.getRange(`A1`).getResizedRange(
                    data.length - 1,  // number of rows
                    (data[0] as any[]).length - 1  // number of columns
                );
  
                // Insert the data
                range.values = data as any[][];
  
                // Activate the new sheet so user sees it
                newSheet.activate();
  
                // Format the first row as a header (optional but nice)
                const headerRange = newSheet.getRange(`A1:${getColumnLetter((data[0] as any[]).length - 1)}1`);
                headerRange.format.font.bold = true;
                headerRange.format.fill.color = "#4472C4";
                headerRange.format.font.color = "white";
  
                // Apply the changes
                await context.sync();
  
                console.log("=== INSERT TO EXCEL SUCCESS ===");
                setStatusMessage({
                    type: 'success',
                    text: `Data inserted successfully into new sheet: "${filename.replace('.xlsx', '')}"`
                });
            }).catch((error) => {
                console.error("Office.js error:", error);
                setStatusMessage({
                    type: 'error',
                    text: `Failed to insert data into Excel: ${error.message}`
                });
            });
  
        } catch (error) {
            console.error("=== INSERT TO EXCEL ERROR ===");
            console.error("Error:", error);
            alert(`Failed to process file: ${error instanceof Error ? error.message : String(error)}`);
        }
    };

    function getColumnLetter(columnNumber: number): string {
        let letter = '';
        while (columnNumber >= 0) {
            letter = String.fromCharCode((columnNumber % 26) + 65) + letter;
            columnNumber = Math.floor(columnNumber / 26) - 1;
        }
        return letter;
    }
    // ===========================================
    // RENDERING - The UI that the user sees
    // ===========================================

    return (
        <div className={styles.container}>
            <Card>
                <CardHeader
                    header={<Text weight="semibold">AI Task Executor</Text>}
                    description={<Text size={200}>Upload files if needed and enter your task request</Text>}
                />
                {/* File upload section */}
                <div style={{ marginBottom: "16px" }}>
                    {/*Hidden file input - triggered when user clicks "Upload Files" button*/}
                    <input
                        type="file"
                        multiple
                        accept=".xlsx,.xls,.csv,.txt"
                        onChange={handleFileSelect}
                        className={styles.fileInput}
                        id="file-upload-input"
                    />
                    {/*Visible upload button - triggers hidden file input*/}
                    <Button
                        appearance="secondary"
                        icon={<ArrowUpload24Regular />}
                        onClick={() => {
                            // Programmatically trigger the hidden file input
                            const fileInput = document.getElementById('file-upload-input') as HTMLInputElement;
                            if (fileInput) {
                                fileInput.click();
                            }
                        }}
                    >
                        Upload Files (Optional)
                    </Button>

                    {/*Display selected files*/}
                    {selectedFiles.length > 0 && (
                        <div className={styles.fileList}>
                            {selectedFiles.map((file, index) => (
                                <div className={styles.fileItem} key={index}>
                                    <span>{file.name}</span>
                                    <Button
                                        appearance="subtle"
                                        icon={<Dismiss24Regular />}
                                        onClick={() => handleFileRemove(file)}
                                    />
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* User request input */}
                <div style={{ marginBottom: "16px" }}>
                    <Textarea
                        placeholder="Describe what you want to do..."
                        value={userRequest}
                        onChange={(e) => setUserRequest(e.target.value)}
                        resize="vertical"
                        rows={4}
                    />
                </div>

                {/* Execute button */}
                <div style={{ marginBottom: "16px" }}>
                    <Button
                        appearance="primary"
                        icon={<Play24Regular />}
                        onClick={handleExecuteTask}
                        disabled={isLoading || !userRequest.trim()}
                    >
                        {isLoading ? "Executing..." : "Execute Task"}
                    </Button>
                </div>
                {/* Status message display */}
                {statusMessage && (
                    <div style={{
                        padding: "12px",
                        borderRadius: "4px",
                        marginBottom: "16px",
                        backgroundColor: statusMessage.type === 'success' 
                            ? tokens.colorPaletteGreenBackground2
                            : statusMessage.type === 'error'
                            ? tokens.colorPaletteRedBackground2
                            : tokens.colorPaletteBlueBackground2,
                        border: `1px solid ${
                            statusMessage.type === 'success'
                                ? tokens.colorPaletteGreenBorder2
                                : statusMessage.type === 'error'
                                ? tokens.colorPaletteRedBorder2
                                : tokens.colorNeutralForeground1
                        }`
                    }}>
                        <Text>{statusMessage.text}</Text>
                        <Button
                            appearance="subtle"
                            size="small"
                            icon={<Dismiss24Regular />}
                            onClick={() => setStatusMessage(null)}
                            style={{ float: "right", marginTop: "-4px" }}
                        />
                    </div>
                )}
            </Card>

            {/* Response display */}
            {response && (
                <Card className={styles.resultsCard}>
                    <CardHeader
                        header={<Text weight="semibold">{response.success ? "Task Completed" : "Task Failed"}</Text>}
                    />

                    {/* Success response */}
                    {response.success && "output" in response && (
                    <div>
                        <Text>Output:</Text>
                        <div className={styles.codePreview}>{response.output}</div>

                        {/* Show generated files if any */}
                        {response.output_files && Object.keys(response.output_files).length > 0 && (
                        <div style={{ marginTop: "12px" }}>
                            <Text weight="semibold">Generated Files:</Text>
                            {Object.keys(response.output_files).map((filename) => (
                            <div key={filename} style={{ marginTop: "8px" }}>
                                <Text>{filename}</Text>
                                <Button
                                    appearance="secondary"
                                    size="small"
                                    onClick={() => handleDownloadFile(filename, response.output_files![filename])}
                                    style={{ marginLeft: "8px" }}
                                >
                                    Insert into Excel
                                </Button>
                            </div>
                            ))}
                        </div>
                        )}
                    </div>
                    )}

                    {/* PERMISSION REQUIRED RESPONSE */}
                    {!response.success && "requires_permission" in response && response.requires_permission && (
                    <div>
                        <Text>{response.explanation}</Text>
                        <div style={{ marginTop: "12px" }}>
                        <Text weight="semibold">Code Preview:</Text>
                        <div className={styles.codePreview}>{response.code_preview}</div>
                        </div>
                        {/* TODO: Add "Approve" and "Deny" buttons in next task */}
                    </div>
                    )}

                    {/* ERROR RESPONSE */}
                    {!response.success && !("requires_permission" in response) && (
                    <div>
                        <Text>{(response as ExecutionErrorResponse).error}</Text>
                        {(response as ExecutionErrorResponse).details && (
                        <Text size={200} style={{ marginTop: "8px" }}>
                            Details: {(response as ExecutionErrorResponse).details}
                        </Text>
                        )}
                    </div>
                    )}
                </Card>
            )}
        </div>
    );
};

export default AIExecutor;