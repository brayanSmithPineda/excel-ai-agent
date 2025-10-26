/**
 * API Service for Backend Communication
 *
 * Handles all HTTP requests to the FastAPI backend for AI code execution.
 */

import { supabase } from '../../lib/supabaseClient'

// ============================================================================
// TYPE DEFINITIONS - Match backend Pydantic schemas
// ============================================================================

export interface ExecuteTaskResponse {
success: true;
output: string;
output_files?: { [filename: string]: string };  // Base64-encoded files
exit_code: number;
}

export interface PermissionRequiredResponse {
success: false;
requires_permission: true;
risk_level: "medium";
explanation: string;
restricted_imports: string[];
code_preview: string;
message: string;
}

export interface ExecutionErrorResponse {
success: false;
error: string;
reason?: string;
details?: string;
output?: string;
}

//Union type for the different response types
export type AIExecutorResponse =
| ExecuteTaskResponse
| PermissionRequiredResponse
| ExecutionErrorResponse;

export interface ExecuteTaskRequest {
userRequest: string;
files?: File[];
operationType?: string;
}

//===========================================
// CONFIGURATION - BACKEND API URL
//===========================================

// ✅ Using HTTPS with mkcert certificates (trusted SSL)
const API_BASE_URL = 'https://127.0.0.1:8003';
const AI_EXECUTOR_ENDPOINT = `${API_BASE_URL}/api/v1/ai-executor/execute-task`;

//===========================================
// AUTHENTICATION HELPERS
//===========================================

// Helper to get current access token
async function getAccessToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token || null
}

// Helper to make authenticated requests
async function makeAuthenticatedRequest(url: string, options: RequestInit): Promise<Response> {
  const token = await getAccessToken()
  
  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  })

  if (response.status === 401) {
    // Token expired - try to refresh
    const { data: { session } } = await supabase.auth.refreshSession()
    
    if (session?.access_token) {
      // Retry with new token
      return await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${session.access_token}`
        }
      })
    }
    
    throw new Error('Session expired - please login again')
  }

    return response
}

//===========================================
// CHAT API FUNCTIONS
//===========================================

export interface ChatRequest {
    message: string;
    conversation_id?: string | null;
    enable_semantic_search?: boolean;
    enable_excel_search?: boolean;
    enable_hybrid_search?: boolean;
}

export interface ChatResponse {
    ai_response: string;
    conversation_id: string;
    
    // Code execution fields
    executed_code?: boolean;
    code_output?: string;
    output_files?: Record<string, string>;  // filename -> base64
    execution_reason?: string;
    
    // NEW: Formula writing fields (Office.js execution)
    write_formulas?: boolean;
    office_js_code?: string;
    formula_reason?: string;
    target_column?: string;
    formula_description?: string;
    
    // Permission request fields
    requires_permission?: boolean;
    risk_level?: string;
    code_preview?: string;
    
    // Search context
    search_results?: {
        semantic_matches: number;
        excel_functions: number;
        workbook_context: boolean;
    };
}

export async function sendChatMessage(
    message: string,
    conversationId: string | null
): Promise<ChatResponse> {
    const token = await getAccessToken()
    
    if (!token) {
        throw new Error('Not authenticated')
    }

    // Extract current workbook data
    let workbookData = null;
    try {
        workbookData = await getCurrentWorkbookData();
    } catch (error) {
        console.warn("Could not extract workbook data:", error);
    }

    const response = await makeAuthenticatedRequest(`${API_BASE_URL}/api/v1/chat/completion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message,
            conversation_id: conversationId,
            workbook_data: workbookData,
            enable_semantic_search: true,
            enable_excel_search: true,
            enable_hybrid_search: true
        })
    })

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
}

//===========================================
// WORKBOOK DATA EXTRACTION
//===========================================
/**
 * Extract current workbook data for AI context
 */
async function getCurrentWorkbookData(): Promise<any> {
    return new Promise((resolve, reject) => {
        Excel.run(async (context) => {
            try {
                const workbook = context.workbook;
                const worksheets = workbook.worksheets;
                const worksheetsData = [];
                
                // Load all worksheets
                worksheets.load("items");
                await context.sync();
                
                // Get the currently active worksheet
                const activeWorksheet = context.workbook.worksheets.getActiveWorksheet();
                activeWorksheet.load("name");
                await context.sync();
                const activeTabName = activeWorksheet.name;
                
                // Extract data from each worksheet
                for (const worksheet of worksheets.items) {
                    const worksheetData: {
                        name: string;
                        data: any[];
                        rowCount?: number;
                        columnCount?: number;
                    } = {
                        name: worksheet.name,
                        data: []
                    };
                    
                    // Get used range
                    const usedRange = worksheet.getUsedRange();
                    usedRange.load("values,rowCount,columnCount");
                    await context.sync();
                    
                    if (usedRange.values) {
                        worksheetData.data = usedRange.values;
                        worksheetData.rowCount = usedRange.rowCount;
                        worksheetData.columnCount = usedRange.columnCount;
                    }
                    
                    worksheetsData.push(worksheetData);
                }
                
                resolve({
                    worksheets: worksheetsData,
                    activeTab: activeTabName,  // ✅ Add active tab context
                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                reject(error);
            }
        });
    });
}

//===========================================
// HELPER FUNCTIONS
//===========================================
/**
 * Retrieve JWT token from Office.js settings storage
 * 
 * Why: We need to get the JWT token from the Office.js settings storage to authenticate the user with the backend.
 * The token is stored in the Office.js settings storage when the user logs in.
 */

function getAuthToken(): string | null {
    try {
        //office.js settings storage is a global object that stores the user's settings
        const settings = Office.context.document.settings;
        const token = settings.get("jwt_token") as string || null;
        // ⚠️ TEMPORARY: For testing without authentication
        // TODO: Remove this after implementing login
        if (!token) {
            console.warn("No JWT token found - using test mode");
            return "test-token-for-development"; // Fake token for testing
        }

        return token;
    } catch (error) {
    console.error("Error getting auth token:", error);
    // ⚠️ TEMPORARY: Return fake token if Office.js fails
    return "test-token-for-development";
    }
}

// ===========================================
// API CALLS - Execute AI Task
// ===========================================

/**
 * Execute a task with the backend.
 * 
 * @param request - User request and optional files
 * @returns Promise with execution results, permission request, or error
 * 
 * Why this function exists:
 * - Encapsulated all API communication logic in one place
 * - Handle file uploads via FormData
 * - Adds authentication headers automatically
 * - Returns typed responses for type safety
*/

export async function executeTask(request: ExecuteTaskRequest): Promise<AIExecutorResponse> {
    try {
        //Step 1: Get the authentication token from Supabase
        const token = await getAccessToken();
        if (!token) {
            return {
                success: false,
                error: "Authentication token not found",
                details: "Please log in to continue"
            };
        }

        //Step 2: Build FormData (required for file uploads)
        //Why? because we are uploading files and json data together
        const formData = new FormData();

        //Add user request as form field
        formData.append("user_request", request.userRequest);

        //Add operation type as form field
        if (request.operationType) {
            formData.append("operation_type", request.operationType);
        }

        //Add files if provided
        if (request.files) {
            request.files.forEach((file) => {
                formData.append("files", file);
            });
        }

        //Step 3: Make the API call with authentication
        const response = await makeAuthenticatedRequest(AI_EXECUTOR_ENDPOINT, {
            method: "POST",
            body: formData
        });

        //Step 4: Parse JSON response
        const data = await response.json();

        //Step 5: Handle HTTP errors
        if (!response.ok) {
            return {
                success: false,
                error: `HTTP ${response.status} ${response.statusText}`,
                details: data.detail || JSON.stringify(data)
            };
        }

        //Step 6: Return typed response
        return data as AIExecutorResponse;
    } catch (error) {
        // More detailed error logging
        console.error("=== API Call Failed ===");
        console.error("Error type:", error?.constructor?.name);
        console.error("Error message:", error instanceof Error ? error.message : String(error));
        console.error("Full error:", error);
        console.error("Endpoint:", AI_EXECUTOR_ENDPOINT);

        // Try to extract more details
        let errorDetails = "Unknown error";
        if (error instanceof TypeError) {
            errorDetails = `Network error: ${error.message}. Check if backend is running and CORS is configured.`;
        } else if (error instanceof Error) {
            errorDetails = error.message;
        }

        return {
            success: false,
            error: "API call failed",
            details: errorDetails
        };
    }
}