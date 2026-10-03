import * as React from "react"
import { addPropertyControls, ControlType } from "framer"
import { motion } from "framer-motion"

type IconName = "signal" | "problem" | "access" | "run" | "learn" | "scale" | "route" | "camera" | "people" | "spark"
type Theme = "light" | "dark"
interface Props { label?: string; icon?: IconName; theme?: Theme; style?: React.CSSProperties }

const paths: Record<IconName, React.ReactNode> = {
    signal: <><path d="M4 12h4l2.2-5 3.6 10 2.2-5H20"/><circle cx="4" cy="12" r="1.5"/><circle cx="20" cy="12" r="1.5"/></>,
    problem: <><circle cx="12" cy="12" r="8"/><path d="M12 7v6M12 17h.01"/></>,
    access: <><circle cx="10" cy="10" r="5"/><path d="m14 14 5 5M4 20c1.6-3 4.2-4.5 7.5-4.5"/></>,
    run: <><rect x="3" y="5" width="6" height="6" rx="2"/><rect x="15" y="13" width="6" height="6" rx="2"/><path d="M9 8h4a4 4 0 0 1 4 4v1"/></>,
    learn: <><path d="M4 19V9M10 19V5M16 19v-7M22 19V3"/><path d="M3 19h20"/></>,
    scale: <><path d="M5 17h4v3H5zM10 12h4v8h-4zM15 7h4v13h-4z"/><path d="m5 11 5-4 4 2 5-5"/></>,
    route: <><circle cx="5" cy="18" r="2"/><circle cx="19" cy="6" r="2"/><path d="M7 18h3a3 3 0 0 0 3-3V9a3 3 0 0 1 3-3h1"/></>,
    camera: <><path d="M4 8h3l1.5-2h7L17 8h3v11H4z"/><circle cx="12" cy="13.5" r="3.5"/></>,
    people: <><circle cx="9" cy="9" r="3"/><circle cx="17" cy="10" r="2.5"/><path d="M3 20c.5-4 2.5-6 6-6s5.5 2 6 6M15 15c3.2 0 5 1.6 5.5 5"/></>,
    spark: <><path d="m12 3 1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5z"/><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7z"/></>,
}

/**
 * @framerSupportedLayoutWidth auto
 * @framerSupportedLayoutHeight auto
 */
export default function IRGSectionPill({ label = "The problem", icon = "problem", theme = "light", style }: Props) {
    const isDark = theme === "dark"
    const gradientId = React.useId().replace(/:/g, "")
    return <motion.div
        style={{ ...style, position: "relative", width: "max-content", minWidth: "max-content", height: 32, display: "flex", alignItems: "center", gap: 8, padding: "3px 12px 3px 3px", borderRadius: 999, color: isDark ? "#FFFFFF" : "#707070", background: isDark ? "rgba(31,31,31,.96)" : "rgba(244,244,244,.96)", boxShadow: isDark ? "0 6px 18px rgba(0,0,0,.20)" : "0 6px 18px rgba(10,10,10,.06)", font: "600 12px/1 \"BDO Grotesk\", sans-serif", boxSizing: "border-box" }}
        initial="rest"
        whileHover="hover"
    >
        <motion.span variants={{ rest: { rotate: 0, x: 0 }, hover: { rotate: -7, x: 1 } }} transition={{ duration: .3, ease: [0.23,1,0.32,1] }} style={{ width: 26, height: 26, display: "grid", placeItems: "center", borderRadius: 999, background: isDark ? "#0A0A0A" : "#FFFFFF", boxShadow: isDark ? "none" : "0 2px 8px rgba(10,10,10,.08)" }}>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke={isDark ? "#FFFFFF" : "url(#" + gradientId + ")"} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <defs><linearGradient id={gradientId} x1="3" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse"><stop stopColor="#FF3131"/><stop offset="1" stopColor="#223DFE"/></linearGradient></defs>
                {paths[icon]}
            </svg>
        </motion.span>
        <span>{label}</span>
    </motion.div>
}

addPropertyControls(IRGSectionPill, {
    label: { type: ControlType.String, title: "Label", defaultValue: "The problem" },
    icon: { type: ControlType.Enum, title: "Icon", options: ["signal","problem","access","run","learn","scale","route","camera","people","spark"], optionTitles: ["Signal","Problem","Access","Run","Learn","Scale","Route","Camera","People","Spark"], defaultValue: "problem" },
    theme: { type: ControlType.Enum, title: "Theme", options: ["light","dark"], optionTitles: ["Light","Dark"], defaultValue: "light" },
})
