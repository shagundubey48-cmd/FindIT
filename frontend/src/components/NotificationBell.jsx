import { Bell } from "lucide-react";
import { Link } from "react-router-dom";
import { useNotifications } from "../hooks/useNotifications";
export default function NotificationBell(){const {unreadCount}=useNotifications();return <Link to="/notifications" className="relative inline-flex rounded-lg p-2 text-slate-600 hover:bg-slate-100" aria-label="Notifications"><Bell size={19}/>{unreadCount>0&&<span className="absolute -right-1 -top-1 rounded-full bg-red-500 px-1.5 text-[10px] font-bold text-white">{unreadCount}</span>}</Link>}

