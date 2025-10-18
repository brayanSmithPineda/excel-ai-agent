import * as React from "react";

// Component imports - our custom components for the AI assistant
import Header from "./Header"; // Header component showing logo and title
import HeroList, { HeroListItem } from "./HeroList"; // List component showing feature highlights
import TextInsertion from "./TextInsertion"; // Component for interacting with Excel text insertion
import ExcelReader from "./ExcelReader"; // Component for testing Excel operations (Day 2 Frontend)
import AIExecutor from "./AIExecutor"; // Component for the AI executor
import ChatComponent from "./ChatComponent"; // Component for the chat interface

import { makeStyles } from "@fluentui/react-components";

import { 
  Brain24Regular,     
  Shield24Regular,    
  DatabaseArrowUpRegular  
} from "@fluentui/react-icons";

// Utility function import - handles inserting text into Excel cells
// This function uses Office.js APIs to interact with the Excel document
import { insertText } from "../taskpane";

// TypeScript interface defining the props (properties) passed to this component
// Props allow parent components to customize how this component behaves
interface AppProps {
  title: string; // The title displayed in the header of the task pane
}

const useStyles = makeStyles({
  root: {
    minHeight: "100vh",
    padding: "16px",
    backgroundColor: "var(--colorNeutralBackground1)",
  },
});

const App: React.FC<AppProps> = (props: AppProps) => {
  const styles = useStyles();
  
  const listItems: HeroListItem[] = [
    {
      icon: <Brain24Regular />,
      primaryText: "AI-powered data cleaning and analysis",
    },
    {
      icon: <Shield24Regular />,
      primaryText: "Enterprise security with full audit logging",
    },
    {
      icon: <DatabaseArrowUpRegular />,
      primaryText: "Direct integrations with business tools",
    },
  ];

  // This creates the visual layout that users see in the Excel task pane
  return (
    <div className={styles.root}>
      <Header 
        logo="assets/logo-filled.png" 
        title={props.title} 
        message="Welcome to your AI Assistant" 
      />
      
      <HeroList
        message="Secure AI assistance for your Excel workflows!"
        items={listItems}
      />
      {/*
        ExcelReader component - Day 2 Frontend: Test Excel operations
        This component tests our excel_operations.ts service by reading data from Excel
        <ExcelReader />

        TextInsertion component provides basic Excel interaction
        This will be replaced with our chat interface and AI features
        insertText function handles the actual Office.js API calls
        <TextInsertion insertText={insertText} />
      */}
      
      {/* AIExecutor component */}
      <AIExecutor />

      {/* ChatComponent component */}
      <ChatComponent />
    </div>
  );
};

export default App;
