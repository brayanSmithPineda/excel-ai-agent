// React import - provides the React library for creating components
import * as React from "react";

// Component imports - our custom components for the AI assistant
import Header from "./Header"; // Header component showing logo and title
import HeroList, { HeroListItem } from "./HeroList"; // List component showing feature highlights
import TextInsertion from "./TextInsertion"; // Component for interacting with Excel text insertion

// Fluent UI imports - Microsoft's design system components
// makeStyles creates CSS-in-JS styles that match Office design language
import { makeStyles } from "@fluentui/react-components";

// Fluent UI icons - provides consistent iconography with Office applications
// These specific icons represent our AI assistant's key features
import { 
  Brain24Regular,      // AI/intelligence icon for smart features
  Shield24Regular,     // Security icon for audit/governance features  
  DatabaseArrow24Regular  // Data integration icon for business connections
} from "@fluentui/react-icons";

// Utility function import - handles inserting text into Excel cells
// This function uses Office.js APIs to interact with the Excel document
import { insertText } from "../taskpane";

// TypeScript interface defining the props (properties) passed to this component
// Props allow parent components to customize how this component behaves
interface AppProps {
  title: string; // The title displayed in the header of the task pane
}

// CSS-in-JS styles using Fluent UI's styling system
// makeStyles creates a React hook that returns CSS classes
const useStyles = makeStyles({
  root: {
    // Ensures the app takes up the full height of the task pane
    // This prevents awkward white space at the bottom
    minHeight: "100vh",
    // Add padding for better spacing within the Excel task pane
    padding: "16px",
    // Ensure consistent background color matching Office theme
    backgroundColor: "var(--colorNeutralBackground1)",
  },
});

// Main App component - the root component of our Excel AI Assistant
// React.FC<AppProps> means this is a React Functional Component that accepts AppProps
const App: React.FC<AppProps> = (props: AppProps) => {
  // Get the CSS classes from our styles hook
  const styles = useStyles();
  
  // Static list of feature highlights for our AI assistant
  // These items showcase the key capabilities to users when they first open the add-in
  // Using const instead of state because these items don't change during runtime
  const listItems: HeroListItem[] = [
    {
      // Brain icon represents AI and intelligent features
      icon: <Brain24Regular />,
      // Highlight the AI-powered data cleaning capabilities
      primaryText: "AI-powered data cleaning and analysis",
    },
    {
      // Shield icon represents security and governance features
      icon: <Shield24Regular />,
      // Emphasize the security and audit features for enterprise users
      primaryText: "Enterprise security with full audit logging",
    },
    {
      // Database arrow icon represents data integration capabilities
      icon: <DatabaseArrow24Regular />,
      // Showcase the business tool integrations (Stripe, NetSuite, etc.)
      primaryText: "Direct integrations with business tools",
    },
  ];

  // JSX return - defines the UI structure of our component
  // This creates the visual layout that users see in the Excel task pane
  return (
    <div className={styles.root}>
      {/* Header component displays logo, title, and welcome message */}
      {/* props.title comes from the parent component and shows in the header */}
      <Header 
        logo="assets/logo-filled.png" 
        title={props.title} 
        message="Welcome to your AI Assistant" 
      />
      
      {/* HeroList component displays our key features with icons */}
      {/* This gives users an immediate understanding of what the add-in can do */}
      <HeroList 
        message="Secure AI assistance for your Excel workflows!" 
        items={listItems} 
      />
      
      {/* TextInsertion component provides basic Excel interaction */}
      {/* This will be replaced with our chat interface and AI features */}
      {/* insertText function handles the actual Office.js API calls */}
      <TextInsertion insertText={insertText} />
    </div>
  );
};

// Export the component so it can be imported and used by other files
// This makes the App component available to index.tsx and other parent components
export default App;
