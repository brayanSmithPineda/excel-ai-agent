/**
 * API Service for Backend Communication
 *
 * Handles all HTTP requests to the FastAPI backend for AI code execution.
 */

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

// ✅ Using HTTPS with mkcert-generated certificates (trusted by system)
const API_BASE_URL = 'https://localhost:8000';
const AI_EXECUTOR_ENDPOINT = `${API_BASE_URL}/api/v1/ai-executor/execute-task`;

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
        //Step 1: Get the authentication token
        const token = getAuthToken();
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

        //Step 3: Make the API call
        const response = await fetch(AI_EXECUTOR_ENDPOINT, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
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