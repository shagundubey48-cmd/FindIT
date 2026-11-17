import { createContext, useCallback, useEffect, useState } from "react";
import api from "../services/api";
export const NotificationContext=createContext(null);
export function NotificationProvider({children}){const [notifications,setNotifications]=useState([]);const [unreadCount,setUnreadCount]=useState(0);
 const refresh=useCallback(async()=>{if(!localStorage.getItem("token")){setNotifications([]);setUnreadCount(0);return;}try{const {data}=await api.get("/notifications");setNotifications(data.notifications||[]);setUnreadCount(data.unread_count||0);}catch{setNotifications([]);setUnreadCount(0);}},[]);
 useEffect(()=>{refresh();},[refresh]);
 const markRead=async id=>{await api.patch(`/notifications/${id}/read`);await refresh();};
 return <NotificationContext.Provider value={{notifications,unreadCount,refresh,markRead}}>{children}</NotificationContext.Provider>;
}

