import { useContext } from "react";
import { NotificationContext } from "../context/NotificationContext";
export function useNotifications(){return useContext(NotificationContext)||{notifications:[],unreadCount:0,refresh:async()=>{},markRead:async()=>{}};}
export default useNotifications;

