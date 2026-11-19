import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getNotifications, markNotificationRead } from "../services/notificationService";

export const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const refresh = useCallback(async () => {
    try {
      const response = await getNotifications();
      const data = response.data;
      setNotifications(Array.isArray(data) ? data : data.notifications || []);
    } catch (error) {
      // Keep the app usable if notifications cannot be loaded.
      setNotifications([]);
    }
  }, []);

  useEffect(() => {
    if (localStorage.getItem("token")) {
      refresh();
    }
  }, [refresh]);

  const markRead = async (id) => {
    await markNotificationRead(id);
    setNotifications((current) =>
      current.map((notification) =>
        notification.id === id ? { ...notification, is_read: true } : notification
      )
    );
  };

  const unreadCount = notifications.filter((notification) => !notification.is_read).length;

  return (
    <NotificationContext.Provider value={{ notifications, unreadCount, refresh, markRead }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotificationContext() {
  return useContext(NotificationContext);
}
