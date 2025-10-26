import * as React from "react";

// Component imports - our custom components for the AI assistant
import Header from "./Header"; // Header component showing logo and title
import HeroList, { HeroListItem } from "./HeroList"; // List component showing feature highlights
import TextInsertion from "./TextInsertion"; // Component for interacting with Excel text insertion
import ExcelReader from "./ExcelReader"; // Component for testing Excel operations (Day 2 Frontend)
import ChatComponent from "./ChatComponent"; // Component for the chat interface
import { LoginComponent } from "./LoginComponent"; // Component for authentication
import { AuthProvider, useAuth } from "../../contexts/AuthContext"; // Authentication context

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

// AppContent component that handles authentication state
const AppContent: React.FC<AppProps> = (props: AppProps) => {
  const styles = useStyles();
  const { user, loading, signOut } = useAuth();
  
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

  // Show loading state
  if (loading) {
    return (
      <div className={styles.root} style={{ textAlign: 'center', padding: '50px' }}>
        <div>Loading...</div>
      </div>
    );
  }

  // Show login form if not authenticated
  if (!user) {
    return (
      <div className={styles.root}>
        <Header 
          logo="assets/logo-filled.png" 
          title={props.title} 
          message="Welcome to your AI Assistant" 
        />
        <LoginComponent />
      </div>
    );
  }

  // Show main app if authenticated
  return (
    <div className={styles.root}>
      <Header 
        logo="assets/logo-filled.png" 
        title={props.title} 
        message={`Welcome, ${user.email}`} 
      />
      
      {/* Logout button */}
      <div style={{ textAlign: 'right', marginBottom: '10px' }}>
        <button 
          onClick={signOut}
          style={{
            padding: '8px 16px',
            backgroundColor: '#d32f2f',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </div>
      
      <HeroList
        message="Secure AI assistance for your Excel workflows!"
        items={listItems}
      />
      

      {/* ChatComponent component */}
      <ChatComponent />
    </div>
  );
};

// Main App component with AuthProvider
const App: React.FC<AppProps> = (props: AppProps) => {
  return (
    <AuthProvider>
      <AppContent {...props} />
    </AuthProvider>
  );
};

export default App;
