/**
 * Excel Operations Service
 * 
 * Handles Office.js operations for reading and writing data to Excel.
 * This service provides a clean interface for Excel interactions,
 * separating Office.js logic from React components.
 * 
 * Key Office.js concepts:
 * - Excel.run() creates a context for Excel operations
 * - context.sync() batches and executes queued commands
 * - load() specifies which properties to read from Excel
 */

/**
 * Read data from the currently selected range in Excel
 * 
 * @returns Promise with array of row data
 * 
 * Example usage:
 *   const data = await readSelectedRange();
 *   console.log(data); // [["Name", "Age"], ["John", 25], ["Jane", 30]]
 */
export async function readSelectedRange(): Promise<any[][]> {
    try {
        return await Excel.run(async (context) => { //Excel is globally available in the Office.js environment beucase we imported in the html file script tag
            // Get the selected range            
            const range = context.workbook.getSelectedRange();

            // Load the values of the range
            range.load("values");

            //Execute the queued commands and return data
            await context.sync();

            //range.values is 2d array: [[row1col1, row1col2], [row2col1, row2col2]]
            return range.values;
        });
    } catch (error) {
        console.error("Error reading selected range:", error);
        throw error;
    }
}

/**
 * Write data to the currently selected range in Excel
 * 
 * @param data - 2D array of data to write
 * 
 * Example usage:
 *   await writeToSelectedRange([["Name", "Age"], ["John", 25], ["Jane", 30]]);
 *   console.log("Data written successfully");
 */
export async function writeToSelectedRange(data: any[][]): Promise<void> {
    try {
        await Excel.run(async (context) => {
        // Get the selected range
        const range = context.workbook.getSelectedRange();

        // Set the values
        // Office.js automatically resizes the range to fit the data
        range.values = data;

        // Execute the write operation
        await context.sync();
        });
    } catch (error) {
        console.error("Error writing to selected range:", error);
        throw new Error(`Failed to write data to Excel: ${error.message}`);
    }
}
/**
 * Read data from a specific sheet and range address
 * 
 * @param sheetName - Name of the worksheet
 * @param rangeAddress - A1-notation address (e.g., "A1:C10")
 * @returns Promise with array of row data
 * 
 * Example usage:
 *   const data = await readRange("Sheet1", "A1:C10");
 */
export async function readRange(sheetName: string, rangeAddress: string): Promise<any[][]> {
    try {
        return await Excel.run(async (context) => {
        // Get the specific worksheet
        const sheet = context.workbook.worksheets.getItem(sheetName);

        // Get the range by address
        const range = sheet.getRange(rangeAddress);

        // Load the values
        range.load("values");

        // Execute and return
        await context.sync();
        return range.values;
        });
    } catch (error) {
        console.error(`Error reading range ${rangeAddress} from sheet ${sheetName}:`, error);
        throw new Error(`Failed to read range: ${error.message}`);
    }
}

/**
 * Get information about the current workbook
 * 
 * @returns Promise with workbook info
 * 
 * Example usage:
 *   const info = await getWorkbookInfo();
 *   console.log(info); // { name: "Sales.xlsx", sheetCount: 3, activeSheet: "Q1" }
 */
export async function getWorkbookInfo(): Promise<{ name: string; sheetCount: number; activeSheet: string }> {
    try {
        return await Excel.run(async (context) => {
            const workbook = context.workbook;
            const sheets = workbook.worksheets;
            const activeSheet = workbook.worksheets.getActiveWorksheet();

            // Load properties we need
            // IMPORTANT: WorksheetCollection doesn't have a "count" property
            // We need to load "items" array and use .length instead
            workbook.load("name");
            sheets.load("items");  // Load the items array (not "count")
            activeSheet.load("name");

            await context.sync();

            return {
                name: workbook.name,
                sheetCount: sheets.items.length,  // Use .items.length to get the count
                activeSheet: activeSheet.name,
            };
        });
    } catch (error) {
        console.error("Error getting workbook info:", error);
        throw new Error(`Failed to get workbook info: ${error.message}`);
    }
}