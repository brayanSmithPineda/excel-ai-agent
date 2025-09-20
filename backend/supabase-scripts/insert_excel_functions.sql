-- Excel Functions Database Population Script
-- This script inserts comprehensive Excel function data into the excel_functions table
-- Run this in Supabase SQL Editor after creating the excel_functions table

INSERT INTO excel_functions (function_name, category, description, syntax, examples, keywords, difficulty_level, excel_versions) VALUES

-- MATH & STATISTICAL FUNCTIONS
('SUM', 'Math', 'Adds all numbers in a range of cells', '=SUM(number1, [number2], ...)', '[{"formula": "=SUM(A1:A10)", "description": "Add all numbers in cells A1 through A10"}]', '{"add", "total", "addition", "plus"}', 'basic', '{"2016+"}'),

('AVERAGE', 'Math', 'Returns the average (arithmetic mean) of its arguments', '=AVERAGE(number1, [number2], ...)', '[{"formula": "=AVERAGE(A1:A10)", "description": "Calculate the average of numbers in A1 through A10"}]', '{"mean", "avg", "arithmetic mean"}', 'basic', '{"2016+"}'),

('COUNT', 'Math', 'Counts the number of cells that contain numbers', '=COUNT(value1, [value2], ...)', '[{"formula": "=COUNT(A1:A10)", "description": "Count how many cells contain numbers in A1:A10"}]', '{"count numbers", "numerical count"}', 'basic', '{"2016+"}'),

('COUNTA', 'Math', 'Counts the number of cells that are not empty', '=COUNTA(value1, [value2], ...)', '[{"formula": "=COUNTA(A1:A10)", "description": "Count non-empty cells in A1:A10"}]', '{"count all", "count non-empty", "count filled"}', 'basic', '{"2016+"}'),

('MAX', 'Math', 'Returns the largest value among the values', '=MAX(number1, [number2], ...)', '[{"formula": "=MAX(A1:A10)", "description": "Find the highest number in A1:A10"}]', '{"maximum", "highest", "largest", "biggest"}', 'basic', '{"2016+"}'),

('MIN', 'Math', 'Returns the smallest value among the values', '=MIN(number1, [number2], ...)', '[{"formula": "=MIN(A1:A10)", "description": "Find the lowest number in A1:A10"}]', '{"minimum", "lowest", "smallest"}', 'basic', '{"2016+"}'),

('SUMIF', 'Math', 'Adds cells that meet a single criteria', '=SUMIF(range, criteria, [sum_range])', '[{"formula": "=SUMIF(A:A, \">100\", B:B)", "description": "Sum values in B where corresponding A value > 100"}]', '{"conditional sum", "sum with criteria", "add if"}', 'intermediate', '{"2016+"}'),

('SUMIFS', 'Math', 'Adds cells that meet multiple criteria', '=SUMIFS(sum_range, criteria_range1, criteria1, [criteria_range2, criteria2], ...)', '[{"formula": "=SUMIFS(C:C, A:A, \">100\", B:B, \"Text\")", "description": "Sum C where A>100 AND B=Text"}]', '{"multiple criteria sum", "conditional sum multiple"}', 'intermediate', '{"2016+"}'),

('COUNTIF', 'Math', 'Counts cells that meet a single criteria', '=COUNTIF(range, criteria)', '[{"formula": "=COUNTIF(A:A, \">100\")", "description": "Count cells in column A that are greater than 100"}]', '{"conditional count", "count with criteria", "count if"}', 'intermediate', '{"2016+"}'),

('COUNTIFS', 'Math', 'Counts cells that meet multiple criteria', '=COUNTIFS(criteria_range1, criteria1, [criteria_range2, criteria2], ...)', '[{"formula": "=COUNTIFS(A:A, \">100\", B:B, \"Text\")", "description": "Count where A>100 AND B=Text"}]', '{"multiple criteria count", "conditional count multiple"}', 'intermediate', '{"2016+"}'),

('ROUND', 'Math', 'Rounds a number to a specified number of digits', '=ROUND(number, num_digits)', '[{"formula": "=ROUND(2.149, 1)", "description": "Rounds 2.149 to 1 decimal place (result: 2.1)"}]', '{"rounding", "decimal places", "precision"}', 'basic', '{"2016+"}'),

('ABS', 'Math', 'Returns the absolute value of a number', '=ABS(number)', '[{"formula": "=ABS(-5)", "description": "Returns 5 (absolute value of -5)"}]', '{"absolute", "positive", "magnitude"}', 'basic', '{"2016+"}'),

-- LOOKUP & REFERENCE FUNCTIONS
('VLOOKUP', 'Lookup', 'Searches for a value in the first column of a table and returns a value in the same row from another column', '=VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup])', '[{"formula": "=VLOOKUP(A2, D:F, 2, FALSE)", "description": "Find exact match for A2 in column D, return value from column E"}]', '{"vertical lookup", "search", "find", "table lookup"}', 'intermediate', '{"2016+"}'),

('HLOOKUP', 'Lookup', 'Searches for a value in the top row of a table and returns a value in the same column from a specified row', '=HLOOKUP(lookup_value, table_array, row_index_num, [range_lookup])', '[{"formula": "=HLOOKUP(A1, 1:3, 2, FALSE)", "description": "Find A1 in row 1, return value from row 2"}]', '{"horizontal lookup", "search horizontal", "row lookup"}', 'intermediate', '{"2016+"}'),

('INDEX', 'Lookup', 'Returns a value from a table based on row and column numbers', '=INDEX(array, row_num, [column_num])', '[{"formula": "=INDEX(B:B, 5)", "description": "Return the value in the 5th row of column B"}]', '{"position", "get value", "array", "coordinates"}', 'intermediate', '{"2016+"}'),

('MATCH', 'Lookup', 'Returns the relative position of an item that matches a specified value', '=MATCH(lookup_value, lookup_array, [match_type])', '[{"formula": "=MATCH(\"Apple\", A:A, 0)", "description": "Find the row number where Apple appears in column A"}]', '{"position", "find position", "locate", "search position"}', 'intermediate', '{"2016+"}'),

('XLOOKUP', 'Lookup', 'Searches a range or array for a match and returns the corresponding item from a second range or array', '=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])', '[{"formula": "=XLOOKUP(A2, D:D, E:E)", "description": "Modern replacement for VLOOKUP - find A2 in column D, return from column E"}]', '{"modern lookup", "advanced lookup", "replacement vlookup"}', 'advanced', '{"2021+"}'),

-- LOGICAL FUNCTIONS
('IF', 'Logical', 'Performs a logical test and returns one value for TRUE and another for FALSE', '=IF(logical_test, [value_if_true], [value_if_false])', '[{"formula": "=IF(A1>10, \"High\", \"Low\")", "description": "If A1 is greater than 10, show High, otherwise Low"}]', '{"condition", "test", "conditional", "decision"}', 'basic', '{"2016+"}'),

('AND', 'Logical', 'Returns TRUE if all arguments are TRUE', '=AND(logical1, [logical2], ...)', '[{"formula": "=AND(A1>5, B1<10)", "description": "TRUE only if A1>5 AND B1<10"}]', '{"all true", "multiple conditions", "both"}', 'intermediate', '{"2016+"}'),

('OR', 'Logical', 'Returns TRUE if any argument is TRUE', '=OR(logical1, [logical2], ...)', '[{"formula": "=OR(A1>5, B1<10)", "description": "TRUE if A1>5 OR B1<10 (or both)"}]', '{"any true", "either", "alternative"}', 'intermediate', '{"2016+"}'),

('IFERROR', 'Logical', 'Returns a value you specify if a formula evaluates to an error', '=IFERROR(value, value_if_error)', '[{"formula": "=IFERROR(A1/B1, \"Error\")", "description": "If A1/B1 causes error, show Error instead"}]', '{"error handling", "catch error", "prevent error"}', 'intermediate', '{"2016+"}'),

-- TEXT FUNCTIONS
('CONCATENATE', 'Text', 'Joins several text strings into one string', '=CONCATENATE(text1, [text2], ...)', '[{"formula": "=CONCATENATE(A1, \" \", B1)", "description": "Combine text from A1, a space, and text from B1"}]', '{"join", "combine", "merge", "connect"}', 'basic', '{"2016+"}'),

('LEFT', 'Text', 'Returns the specified number of characters from the start of a text string', '=LEFT(text, [num_chars])', '[{"formula": "=LEFT(\"Hello\", 3)", "description": "Returns Hel (first 3 characters)"}]', '{"beginning", "start", "first characters"}', 'basic', '{"2016+"}'),

('RIGHT', 'Text', 'Returns the specified number of characters from the end of a text string', '=RIGHT(text, [num_chars])', '[{"formula": "=RIGHT(\"Hello\", 3)", "description": "Returns llo (last 3 characters)"}]', '{"end", "last characters", "suffix"}', 'basic', '{"2016+"}'),

('LEN', 'Text', 'Returns the number of characters in a text string', '=LEN(text)', '[{"formula": "=LEN(\"Hello\")", "description": "Returns 5 (number of characters in Hello)"}]', '{"length", "count characters", "string length"}', 'basic', '{"2016+"}'),

('UPPER', 'Text', 'Converts text to uppercase', '=UPPER(text)', '[{"formula": "=UPPER(\"hello\")", "description": "Returns HELLO"}]', '{"uppercase", "capital", "caps"}', 'basic', '{"2016+"}'),

('LOWER', 'Text', 'Converts text to lowercase', '=LOWER(text)', '[{"formula": "=LOWER(\"HELLO\")", "description": "Returns hello"}]', '{"lowercase", "small letters"}', 'basic', '{"2016+"}'),

('TRIM', 'Text', 'Removes extra spaces from text', '=TRIM(text)', '[{"formula": "=TRIM(\" Hello World \")", "description": "Returns Hello World (removes leading/trailing spaces)"}]', '{"remove spaces", "clean", "whitespace"}', 'basic', '{"2016+"}'),

-- DATE & TIME FUNCTIONS

('TODAY', 'Date', 'Returns the current date', '=TODAY()', '[{"formula": "=TODAY()", "description": "Returns todays date"}]', '{"current date", "todays date", "now"}', 'basic', '{"2016+"}'),

('NOW', 'Date', 'Returns the current date and time', '=NOW()', '[{"formula": "=NOW()", "description": "Returns current date and time"}]', '{"current time", "date time", "timestamp"}', 'basic', '{"2016+"}'),

('DATE', 'Date', 'Returns a date from year, month, and day values', '=DATE(year, month, day)', '[{"formula": "=DATE(2024, 12, 25)", "description": "Returns December 25, 2024"}]', '{"create date", "build date", "construct date"}', 'basic', '{"2016+"}'),

('YEAR', 'Date', 'Returns the year of a date', '=YEAR(serial_number)', '[{"formula": "=YEAR(TODAY())", "description": "Returns the current year"}]', '{"extract year", "get year"}', 'basic', '{"2016+"}'),

-- ADVANCED/MODERN FUNCTIONS
('FILTER', 'Advanced', 'Filters a range of data based on criteria you define', '=FILTER(array, include, [if_empty])', '[{"formula": "=FILTER(A:C, B:B>100)", "description": "Return rows where column B > 100"}]', '{"dynamic filter", "conditional filter", "array"}', 'advanced', '{"2021+"}'),

('UNIQUE', 'Advanced', 'Returns a list of unique values from a range or array', '=UNIQUE(array, [by_col], [exactly_once])', '[{"formula": "=UNIQUE(A:A)", "description": "Returns unique values from column A"}]', '{"distinct", "remove duplicates", "unique values"}', 'advanced', '{"2021+"}'),

-- MORE MATH & STATISTICAL FUNCTIONS
('MEDIAN', 'Math', 'Returns the median of the given numbers', '=MEDIAN(number1, [number2], ...)', '[{"formula": "=MEDIAN(A1:A10)", "description": "Find the middle value in the range A1:A10"}]', '{"middle", "median", "middle value", "50th percentile"}', 'intermediate', '{"2016+"}'),

('MODE', 'Math', 'Returns the most common value in a data set', '=MODE(number1, [number2], ...)', '[{"formula": "=MODE(A1:A10)", "description": "Find the most frequently occurring number"}]', '{"most common", "frequent", "mode"}', 'intermediate', '{"2016+"}'),

('STDEV', 'Math', 'Estimates standard deviation based on a sample', '=STDEV(number1, [number2], ...)', '[{"formula": "=STDEV(A1:A10)", "description": "Calculate standard deviation of sample data"}]', '{"standard deviation", "variance", "spread"}', 'advanced', '{"2016+"}'),

('VAR', 'Math', 'Estimates variance based on a sample', '=VAR(number1, [number2], ...)', '[{"formula": "=VAR(A1:A10)", "description": "Calculate variance of sample data"}]', '{"variance", "variability", "spread"}', 'advanced', '{"2016+"}'),

('PERCENTILE', 'Math', 'Returns the k-th percentile of values in a range', '=PERCENTILE(array, k)', '[{"formula": "=PERCENTILE(A1:A10, 0.9)", "description": "Find the 90th percentile of values"}]', '{"percentile", "quantile", "ranking"}', 'advanced', '{"2016+"}'),

('RANK', 'Math', 'Returns the rank of a number in a list of numbers', '=RANK(number, ref, [order])', '[{"formula": "=RANK(A1, A:A, 0)", "description": "Find the rank of A1 in column A (descending)"}]', '{"ranking", "position", "order"}', 'intermediate', '{"2016+"}'),

('PRODUCT', 'Math', 'Multiplies all the numbers given as arguments', '=PRODUCT(number1, [number2], ...)', '[{"formula": "=PRODUCT(A1:A5)", "description": "Multiply all numbers in A1 through A5"}]', '{"multiply", "multiplication", "product"}', 'basic', '{"2016+"}'),

('POWER', 'Math', 'Returns the result of a number raised to a power', '=POWER(number, power)', '[{"formula": "=POWER(2, 3)", "description": "Returns 8 (2 to the power of 3)"}]', '{"exponent", "power", "raise to power"}', 'basic', '{"2016+"}'),

('SQRT', 'Math', 'Returns a positive square root', '=SQRT(number)', '[{"formula": "=SQRT(16)", "description": "Returns 4 (square root of 16)"}]', '{"square root", "root", "radical"}', 'basic', '{"2016+"}'),

('MOD', 'Math', 'Returns the remainder from division', '=MOD(number, divisor)', '[{"formula": "=MOD(10, 3)", "description": "Returns 1 (remainder when 10 is divided by 3)"}]', '{"remainder", "modulus", "division remainder"}', 'intermediate', '{"2016+"}'),

('INT', 'Math', 'Rounds a number down to the nearest integer', '=INT(number)', '[{"formula": "=INT(8.9)", "description": "Returns 8 (rounds down to nearest integer)"}]', '{"integer", "round down", "floor"}', 'basic', '{"2016+"}'),

('TRUNC', 'Math', 'Truncates a number to an integer by removing the fractional part', '=TRUNC(number, [num_digits])', '[{"formula": "=TRUNC(8.9)", "description": "Returns 8 (removes decimal part)"}]', '{"truncate", "remove decimal", "cut off"}', 'basic', '{"2016+"}'),

('CEILING', 'Math', 'Rounds a number up to the nearest integer or multiple of significance', '=CEILING(number, significance)', '[{"formula": "=CEILING(4.3, 1)", "description": "Returns 5 (rounds up to nearest integer)"}]', '{"round up", "ceiling", "round to multiple"}', 'intermediate', '{"2016+"}'),

('FLOOR', 'Math', 'Rounds a number down to the nearest integer or multiple of significance', '=FLOOR(number, significance)', '[{"formula": "=FLOOR(4.7, 1)", "description": "Returns 4 (rounds down to nearest integer)"}]', '{"round down", "floor", "round to multiple"}', 'intermediate', '{"2016+"}'),

-- MORE LOOKUP & REFERENCE FUNCTIONS
('CHOOSE', 'Lookup', 'Uses an index number to return a value from a list of values', '=CHOOSE(index_num, value1, [value2], ...)', '[{"formula": "=CHOOSE(2, \"Red\", \"Blue\", \"Green\")", "description": "Returns Blue (the 2nd option)"}]', '{"select", "pick", "index choice"}', 'intermediate', '{"2016+"}'),

('INDIRECT', 'Lookup', 'Returns a reference indicated by a text string', '=INDIRECT(ref_text, [a1])', '[{"formula": "=INDIRECT(\"A\" & ROW())", "description": "Creates dynamic cell reference"}]', '{"dynamic reference", "text to reference", "indirect reference"}', 'advanced', '{"2016+"}'),

('OFFSET', 'Lookup', 'Returns a reference to a range that is a specified number of rows and columns from a cell or range of cells', '=OFFSET(reference, rows, cols, [height], [width])', '[{"formula": "=OFFSET(A1, 2, 1)", "description": "Returns reference 2 rows down and 1 column right from A1"}]', '{"dynamic range", "offset reference", "relative reference"}', 'advanced', '{"2016+"}'),

('ROW', 'Lookup', 'Returns the row number of a reference', '=ROW([reference])', '[{"formula": "=ROW(A5)", "description": "Returns 5 (row number of A5)"}]', '{"row number", "current row", "row index"}', 'intermediate', '{"2016+"}'),

('COLUMN', 'Lookup', 'Returns the column number of a reference', '=COLUMN([reference])', '[{"formula": "=COLUMN(D1)", "description": "Returns 4 (column D is the 4th column)"}]', '{"column number", "current column", "column index"}', 'intermediate', '{"2016+"}'),

('TRANSPOSE', 'Lookup', 'Returns a vertical range of cells as a horizontal range, or vice versa', '=TRANSPOSE(array)', '[{"formula": "=TRANSPOSE(A1:A5)", "description": "Convert vertical range to horizontal"}]', '{"transpose", "flip", "rotate", "pivot"}', 'advanced', '{"2016+"}'),

('ROWS', 'Lookup', 'Returns the number of rows in a reference', '=ROWS(array)', '[{"formula": "=ROWS(A1:A10)", "description": "Returns 10 (number of rows in range)"}]', '{"count rows", "row count", "range height"}', 'intermediate', '{"2016+"}'),

('COLUMNS', 'Lookup', 'Returns the number of columns in a reference', '=COLUMNS(array)', '[{"formula": "=COLUMNS(A1:D1)", "description": "Returns 4 (number of columns in range)"}]', '{"count columns", "column count", "range width"}', 'intermediate', '{"2016+"}'),

-- MORE LOGICAL FUNCTIONS
('NOT', 'Logical', 'Reverses the logic of its argument', '=NOT(logical)', '[{"formula": "=NOT(A1>10)", "description": "TRUE if A1 is NOT greater than 10"}]', '{"reverse", "opposite", "negate"}', 'intermediate', '{"2016+"}'),

('IFS', 'Logical', 'Checks multiple conditions and returns a value corresponding to the first TRUE condition', '=IFS([logical_test1, value_if_true1], [logical_test2, value_if_true2], ...)', '[{"formula": "=IFS(A1>90, \"A\", A1>80, \"B\", A1>70, \"C\")", "description": "Grade based on score in A1"}]', '{"multiple if", "nested if", "conditions"}', 'advanced', '{"2019+"}'),

('SWITCH', 'Logical', 'Evaluates an expression against a list of values and returns the result corresponding to the first matching value', '=SWITCH(expression, value1, result1, [value2, result2], ..., [default])', '[{"formula": "=SWITCH(A1, 1, \"One\", 2, \"Two\", \"Other\")", "description": "Return text based on number in A1"}]', '{"switch case", "multiple choice", "case statement"}', 'advanced', '{"2019+"}'),

('IFNA', 'Logical', 'Returns the value you specify if the expression resolves to #N/A', '=IFNA(value, value_if_na)', '[{"formula": "=IFNA(VLOOKUP(A1, B:C, 2, 0), \"Not Found\")", "description": "Handle #N/A errors from VLOOKUP"}]', '{"handle na", "not available", "na error"}', 'intermediate', '{"2016+"}'),

('ISBLANK', 'Logical', 'Returns TRUE if the value is blank', '=ISBLANK(value)', '[{"formula": "=ISBLANK(A1)", "description": "Check if cell A1 is empty"}]', '{"is empty", "blank check", "empty cell"}', 'basic', '{"2016+"}'),

('ISNUMBER', 'Logical', 'Returns TRUE if the value is a number', '=ISNUMBER(value)', '[{"formula": "=ISNUMBER(A1)", "description": "Check if A1 contains a number"}]', '{"is numeric", "number check", "validate number"}', 'basic', '{"2016+"}'),

('ISTEXT', 'Logical', 'Returns TRUE if the value is text', '=ISTEXT(value)', '[{"formula": "=ISTEXT(A1)", "description": "Check if A1 contains text"}]', '{"is string", "text check", "validate text"}', 'basic', '{"2016+"}'),

('ISERROR', 'Logical', 'Returns TRUE if the value is any error value', '=ISERROR(value)', '[{"formula": "=ISERROR(A1/B1)", "description": "Check if division results in error"}]', '{"error check", "is error", "validate calculation"}', 'intermediate', '{"2016+"}'),

('ISNA', 'Logical', 'Returns TRUE if the value is the #N/A error value', '=ISNA(value)', '[{"formula": "=ISNA(VLOOKUP(A1, B:C, 2, 0))", "description": "Check if VLOOKUP returns #N/A"}]', '{"not available", "na check", "lookup error"}', 'intermediate', '{"2016+"}'),

-- MORE TEXT FUNCTIONS
('MID', 'Text', 'Returns characters from the middle of a text string', '=MID(text, start_num, num_chars)', '[{"formula": "=MID(\"Hello\", 2, 3)", "description": "Returns ell (3 chars starting at position 2)"}]', '{"middle", "substring", "extract"}', 'intermediate', '{"2016+"}'),

('SUBSTITUTE', 'Text', 'Substitutes new text for old text in a text string', '=SUBSTITUTE(text, old_text, new_text, [instance_num])', '[{"formula": "=SUBSTITUTE(\"Hello World\", \"o\", \"0\")", "description": "Replace o with 0: Hell0 W0rld"}]', '{"replace", "substitute", "change text"}', 'intermediate', '{"2016+"}'),

('REPLACE', 'Text', 'Replaces characters within text', '=REPLACE(old_text, start_num, num_chars, new_text)', '[{"formula": "=REPLACE(\"Hello\", 2, 2, \"XX\")", "description": "Replace characters 2-3 with XX: HXXlo"}]', '{"replace characters", "overwrite", "change part"}', 'intermediate', '{"2016+"}'),

('FIND', 'Text', 'Finds one text string within another (case-sensitive)', '=FIND(find_text, within_text, [start_num])', '[{"formula": "=FIND(\"o\", \"Hello\")", "description": "Returns 5 (position of o in Hello)"}]', '{"search", "locate", "position", "case sensitive"}', 'intermediate', '{"2016+"}'),

('SEARCH', 'Text', 'Finds one text string within another (case-insensitive)', '=SEARCH(find_text, within_text, [start_num])', '[{"formula": "=SEARCH(\"O\", \"hello\")", "description": "Returns 5 (finds O in hello, case-insensitive)"}]', '{"search", "locate", "position", "case insensitive"}', 'intermediate', '{"2016+"}'),

('TEXT', 'Text', 'Formats a number and converts it to text', '=TEXT(value, format_text)', '[{"formula": "=TEXT(1234.5, \"$#,##0.00\")", "description": "Returns $1,234.50"}]', '{"format", "convert", "number to text"}', 'intermediate', '{"2016+"}'),

('VALUE', 'Text', 'Converts a text string that represents a number to a number', '=VALUE(text)', '[{"formula": "=VALUE(\"123\")", "description": "Converts text 123 to number 123"}]', '{"text to number", "convert", "parse number"}', 'basic', '{"2016+"}'),

('PROPER', 'Text', 'Capitalizes the first letter in each word of a text value', '=PROPER(text)', '[{"formula": "=PROPER(\"hello world\")", "description": "Returns Hello World"}]', '{"title case", "capitalize", "proper case"}', 'basic', '{"2016+"}'),

('CLEAN', 'Text', 'Removes all nonprintable characters from text', '=CLEAN(text)', '[{"formula": "=CLEAN(A1)", "description": "Remove non-printable characters from A1"}]', '{"clean text", "remove characters", "sanitize"}', 'intermediate', '{"2016+"}'),

('EXACT', 'Text', 'Compares two text strings and returns TRUE if they are exactly the same', '=EXACT(text1, text2)', '[{"formula": "=EXACT(\"Hello\", \"hello\")", "description": "Returns FALSE (case-sensitive comparison)"}]', '{"exact match", "compare text", "case sensitive"}', 'intermediate', '{"2016+"}'),

('REPT', 'Text', 'Repeats text a given number of times', '=REPT(text, number_times)', '[{"formula": "=REPT(\"*\", 5)", "description": "Returns ***** (5 asterisks)"}]', '{"repeat", "duplicate", "multiply text"}', 'basic', '{"2016+"}'),

('CHAR', 'Text', 'Returns the character specified by the code number', '=CHAR(number)', '[{"formula": "=CHAR(65)", "description": "Returns A (ASCII character 65)"}]', '{"ascii", "character code", "special character"}', 'intermediate', '{"2016+"}'),

('CODE', 'Text', 'Returns a numeric code for the first character in a text string', '=CODE(text)', '[{"formula": "=CODE(\"A\")", "description": "Returns 65 (ASCII code for A)"}]', '{"ascii code", "character code", "text to number"}', 'intermediate', '{"2016+"}'),

('TEXTJOIN', 'Text', 'Joins the text from multiple ranges and/or strings with a delimiter', '=TEXTJOIN(delimiter, ignore_empty, text1, [text2], ...)', '[{"formula": "=TEXTJOIN(\", \", TRUE, A1:A5)", "description": "Join A1:A5 with commas, ignoring empty cells"}]', '{"join with delimiter", "concatenate with separator", "merge text"}', 'advanced', '{"2019+"}'),

('CONCAT', 'Text', 'Combines the text from multiple ranges and/or strings', '=CONCAT(text1, [text2], ...)', '[{"formula": "=CONCAT(A1:A5)", "description": "Combine all text in A1:A5 without separator"}]', '{"combine", "merge", "concatenate range"}', 'intermediate', '{"2019+"}'),

-- MORE DATE & TIME FUNCTIONS
('MONTH', 'Date', 'Returns the month of a date', '=MONTH(serial_number)', '[{"formula": "=MONTH(TODAY())", "description": "Returns the current month number"}]', '{"extract month", "get month"}', 'basic', '{"2016+"}'),

('DAY', 'Date', 'Returns the day of a date', '=DAY(serial_number)', '[{"formula": "=DAY(TODAY())", "description": "Returns the current day of month"}]', '{"extract day", "get day"}', 'basic', '{"2016+"}'),

('HOUR', 'Date', 'Returns the hour of a time value', '=HOUR(serial_number)', '[{"formula": "=HOUR(NOW())", "description": "Returns the current hour (0-23)"}]', '{"extract hour", "get hour", "time component"}', 'basic', '{"2016+"}'),

('MINUTE', 'Date', 'Returns the minutes of a time value', '=MINUTE(serial_number)', '[{"formula": "=MINUTE(NOW())", "description": "Returns the current minute (0-59)"}]', '{"extract minute", "get minute", "time component"}', 'basic', '{"2016+"}'),

('SECOND', 'Date', 'Returns the seconds of a time value', '=SECOND(serial_number)', '[{"formula": "=SECOND(NOW())", "description": "Returns the current second (0-59)"}]', '{"extract second", "get second", "time component"}', 'basic', '{"2016+"}'),

('TIME', 'Date', 'Returns the decimal number for a particular time', '=TIME(hour, minute, second)', '[{"formula": "=TIME(12, 30, 0)", "description": "Creates time value for 12:30:00"}]', '{"create time", "build time", "construct time"}', 'basic', '{"2016+"}'),

('DATEDIF', 'Date', 'Calculates the difference between two dates', '=DATEDIF(start_date, end_date, unit)', '[{"formula": "=DATEDIF(A1, TODAY(), \"Y\")", "description": "Years between date in A1 and today"}]', '{"date difference", "age", "duration", "time between"}', 'intermediate', '{"2016+"}'),

('WEEKDAY', 'Date', 'Returns the day of the week', '=WEEKDAY(serial_number, [return_type])', '[{"formula": "=WEEKDAY(TODAY())", "description": "Returns 1-7 representing day of week"}]', '{"day of week", "weekday number"}', 'intermediate', '{"2016+"}'),

('WORKDAY', 'Date', 'Returns a date that is the indicated number of working days before or after a date', '=WORKDAY(start_date, days, [holidays])', '[{"formula": "=WORKDAY(TODAY(), 10)", "description": "Date that is 10 business days from today"}]', '{"business days", "working days", "exclude weekends"}', 'intermediate', '{"2016+"}'),

('NETWORKDAYS', 'Date', 'Returns the number of working days between two dates', '=NETWORKDAYS(start_date, end_date, [holidays])', '[{"formula": "=NETWORKDAYS(A1, B1)", "description": "Count business days between A1 and B1"}]', '{"business days count", "working days count", "exclude weekends"}', 'intermediate', '{"2016+"}'),

('EOMONTH', 'Date', 'Returns the serial number for the last day of the month', '=EOMONTH(start_date, months)', '[{"formula": "=EOMONTH(TODAY(), 0)", "description": "Last day of current month"}]', '{"end of month", "last day", "month end"}', 'intermediate', '{"2016+"}'),

('DATEVALUE', 'Date', 'Converts a date in the form of text to a date', '=DATEVALUE(date_text)', '[{"formula": "=DATEVALUE(\"12/25/2024\")", "description": "Convert text date to Excel date"}]', '{"text to date", "parse date", "convert date"}', 'basic', '{"2016+"}'),

('TIMEVALUE', 'Date', 'Converts a time in the form of text to a time', '=TIMEVALUE(time_text)', '[{"formula": "=TIMEVALUE(\"12:30 PM\")", "description": "Convert text time to Excel time"}]', '{"text to time", "parse time", "convert time"}', 'basic', '{"2016+"}'),

-- FINANCIAL FUNCTIONS
('PMT', 'Financial', 'Returns the payment for a loan based on constant payments and constant interest rate', '=PMT(rate, nper, pv, [fv], [type])', '[{"formula": "=PMT(0.05/12, 360, 200000)", "description": "Monthly payment for $200k loan at 5% for 30 years"}]', '{"loan payment", "mortgage", "monthly payment"}', 'intermediate', '{"2016+"}'),

('PV', 'Financial', 'Returns the present value of an investment', '=PV(rate, nper, pmt, [fv], [type])', '[{"formula": "=PV(0.08, 10, -1000)", "description": "Present value of $1000 annual payments at 8%"}]', '{"present value", "investment value", "pv"}', 'intermediate', '{"2016+"}'),

('FV', 'Financial', 'Returns the future value of an investment', '=FV(rate, nper, pmt, [pv], [type])', '[{"formula": "=FV(0.06, 10, -200)", "description": "Future value of $200 monthly payments at 6%"}]', '{"future value", "investment growth", "fv"}', 'intermediate', '{"2016+"}'),

('NPV', 'Financial', 'Returns the net present value of an investment', '=NPV(rate, value1, [value2], ...)', '[{"formula": "=NPV(0.10, -1000, 300, 400, 300)", "description": "NPV of cash flows at 10% discount rate"}]', '{"net present value", "npv", "investment analysis"}', 'advanced', '{"2016+"}'),

('IRR', 'Financial', 'Returns the internal rate of return', '=IRR(values, [guess])', '[{"formula": "=IRR(A1:A5)", "description": "Internal rate of return for cash flows in A1:A5"}]', '{"internal rate of return", "irr", "rate of return"}', 'advanced', '{"2016+"}'),

('RATE', 'Financial', 'Returns the interest rate per period of an annuity', '=RATE(nper, pmt, pv, [fv], [type], [guess])', '[{"formula": "=RATE(360, -1200, 200000)", "description": "Interest rate for loan with given payments"}]', '{"interest rate", "loan rate", "annual rate"}', 'advanced', '{"2016+"}'),

('NPER', 'Financial', 'Returns the number of periods for an investment', '=NPER(rate, pmt, pv, [fv], [type])', '[{"formula": "=NPER(0.12/12, -100, -1000, 10000)", "description": "Number of payments to reach target value"}]', '{"number of periods", "payment count", "loan term"}', 'intermediate', '{"2016+"}'),

-- MORE ADVANCED/MODERN FUNCTIONS
('SORT', 'Advanced', 'Sorts the contents of a range or array', '=SORT(array, [sort_index], [sort_order], [by_col])', '[{"formula": "=SORT(A:B, 1, 1)", "description": "Sort A:B by column 1 ascending"}]', '{"arrange", "order", "alphabetize"}', 'advanced', '{"2021+"}'),

('SORTBY', 'Advanced', 'Sorts the contents of a range or array based on the values in a corresponding range or array', '=SORTBY(array, by_array1, [sort_order1], [by_array2, sort_order2], ...)', '[{"formula": "=SORTBY(A:B, C:C, -1)", "description": "Sort A:B by column C in descending order"}]', '{"sort by column", "custom sort", "sort by criteria"}', 'advanced', '{"2021+"}'),

('SEQUENCE', 'Advanced', 'Generates a list of sequential numbers in an array', '=SEQUENCE(rows, [columns], [start], [step])', '[{"formula": "=SEQUENCE(5, 1, 10, 2)", "description": "Generate 5 numbers starting at 10, step by 2"}]', '{"generate sequence", "number series", "create list"}', 'advanced', '{"2021+"}'),

('RANDARRAY', 'Advanced', 'Returns an array of random numbers', '=RANDARRAY([rows], [columns], [min], [max], [whole_number])', '[{"formula": "=RANDARRAY(5, 2, 1, 100, TRUE)", "description": "5x2 array of random whole numbers 1-100"}]', '{"random numbers", "generate random", "random array"}', 'advanced', '{"2021+"}'),

('LET', 'Advanced', 'Assigns names to calculation results and allows storing intermediate calculations, values, or defining names inside a formula', '=LET(name1, name1_value, [name2, name2_value], ..., calculation)', '[{"formula": "=LET(x, A1*2, y, B1*3, x+y)", "description": "Define variables x and y, then calculate x+y"}]', '{"variables", "define names", "intermediate calculations"}', 'advanced', '{"2021+"}'),

('LAMBDA', 'Advanced', 'Creates custom reusable functions', '=LAMBDA([parameter1, parameter2, ...], calculation)', '[{"formula": "=LAMBDA(x, x*2)(A1)", "description": "Create function that doubles a value"}]', '{"custom function", "reusable formula", "function definition"}', 'advanced', '{"2021+"}'),

('AGGREGATE', 'Math', 'Returns an aggregate in a list or database', '=AGGREGATE(function_num, options, array, [k])', '[{"formula": "=AGGREGATE(1, 5, A1:A10)", "description": "Average ignoring hidden rows and errors"}]', '{"aggregate", "summary with options", "ignore errors"}', 'advanced', '{"2016+"}'),

('SUBTOTAL', 'Math', 'Returns a subtotal in a list or database', '=SUBTOTAL(function_num, ref1, [ref2], ...)', '[{"formula": "=SUBTOTAL(109, A2:A100)", "description": "Sum visible cells only (ignores filtered rows)"}]', '{"subtotal", "filtered sum", "visible cells only"}', 'intermediate', '{"2016+"}'),

-- RANDOM & PROBABILITY FUNCTIONS
('RAND', 'Math', 'Returns a random number between 0 and 1', '=RAND()', '[{"formula": "=RAND()", "description": "Generate random decimal between 0 and 1"}]', '{"random", "random decimal", "probability"}', 'basic', '{"2016+"}'),

('RANDBETWEEN', 'Math', 'Returns a random number between the numbers you specify', '=RANDBETWEEN(bottom, top)', '[{"formula": "=RANDBETWEEN(1, 100)", "description": "Random whole number between 1 and 100"}]', '{"random integer", "random range", "random between"}', 'basic', '{"2016+"}');

-- Verify the insert was successful
SELECT COUNT(*) as total_functions FROM excel_functions;
SELECT category, COUNT(*) as function_count FROM excel_functions GROUP BY category ORDER BY function_count DESC;