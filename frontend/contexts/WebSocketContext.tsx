import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { WS_URL } from '../lib/api';

interface WebSocketContextType {
  isConnected: boolean;
  notifications: any[];
  sendMessage: (message: any) => void;
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const connect = () => {
    try {
      const ws = new WebSocket(`${WS_URL}/ws`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setReconnectAttempts(0);
        setSocket(ws);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setSocket(null);
        
        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts < 5) {
          const delay = Math.pow(2, reconnectAttempts) * 1000;
          setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, delay);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  };

  const handleMessage = (data: any) => {
    switch (data.type) {
      case 'notification':
        setNotifications(prev => [...prev, data.payload]);
        break;
      case 'data_update':
        // Handle real-time data updates
        // This could trigger SWR revalidation or update local state
        break;
      case 'model_update':
        // Handle ML model updates
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const sendMessage = (message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  };

  const subscribe = (channel: string) => {
    sendMessage({
      type: 'subscribe',
      channel: channel,
    });
  };

  const unsubscribe = (channel: string) => {
    sendMessage({
      type: 'unsubscribe',
      channel: channel,
    });
  };

  useEffect(() => {
    connect();
    
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, []);

  const value: WebSocketContextType = {
    isConnected,
    notifications,
    sendMessage,
    subscribe,
    unsubscribe,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}
