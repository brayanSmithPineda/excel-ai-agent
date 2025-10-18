/**
 * ExcelReader Component
 * 
 * A simple component to test our Excel operations service.
 * This demonstrates reading data from Excel and displaying it.
 */

import * as React from "react";
import { Button, Card, CardHeader, Text, makeStyles, tokens } from "@fluentui/react-components";
import { DocumentText24Regular } from "@fluentui/react-icons";
import { readSelectedRange, getWorkbookInfo } from "../services/excel_operations";

const useStyles = makeStyles({
    container: {
        marginTop: tokens.spacingVerticalL,
    },
    output: {
        marginTop: tokens.spacingVerticalM,
        padding: tokens.spacingVerticalM,
        backgroundColor: tokens.colorNeutralBackground3,
        borderRadius: tokens.borderRadiusMedium,
        fontFamily: "monospace",
        fontSize: tokens.fontSizeBase200,
        whiteSpace: "pre-wrap",
        maxHeight: "300px",
        overflowY: "auto",
    },
    buttonGroup: {
        display: "flex",
        gap: tokens.spacingHorizontalS,
        marginTop: tokens.spacingVerticalM,
    },
});

const ExcelReader: React.FC = () => {
    const styles = useStyles();
    const [output, setOutput] = React.useState<string>("");
    const [isLoading, setIsLoading] = React.useState<boolean>(false);

    /**
     * Read data from selected range and display it
     */
    const handleReadSelection = async () => {
        setIsLoading(true);
        try {
        const data = await readSelectedRange();
        setOutput(`Selected Range Data:\n${JSON.stringify(data, null, 2)}`);
        } catch (error) {
        setOutput(`Error: ${error.message}`);
        } finally {
        setIsLoading(false);
        }
    };

    /**
     * Get workbook information and display it
     */
    const handleGetWorkbookInfo = async () => {
        setIsLoading(true);
        try {
        const info = await getWorkbookInfo();
        setOutput(`Workbook Info:\n${JSON.stringify(info, null, 2)}`);
        } catch (error) {
        setOutput(`Error: ${error.message}`);
        } finally {
        setIsLoading(false);
        }
    };

    return (
        <div className={styles.container}>
        <Card>
            <CardHeader
            header={<Text weight="semibold">Test Excel Operations</Text>}
            description={<Text size={200}>Try reading data from Excel</Text>}
            />

            <div className={styles.buttonGroup}>
            <Button
                appearance="primary"
                icon={<DocumentText24Regular />}
                onClick={handleReadSelection}
                disabled={isLoading}
            >
                Read Selection
            </Button>

            <Button appearance="secondary" onClick={handleGetWorkbookInfo} disabled={isLoading}>
                Get Workbook Info
            </Button>
            </div>

            {output && (
            <div className={styles.output}>
                <Text>{output}</Text>
            </div>
            )}
        </Card>
        </div>
    );
};

export default ExcelReader;
