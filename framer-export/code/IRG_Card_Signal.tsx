import * as React from "react"
import { addPropertyControls, ControlType, useIsStaticRenderer } from "framer"
import { motion, useReducedMotion } from "framer-motion"

type Mode = "oneoff" | "always" | "access" | "run" | "learn" | "scale"
interface Props { mode?: Mode; style?: React.CSSProperties }

const gradient = "linear-gradient(135deg, #FF3131 0%, #223DFE 100%)"
const people = [
    "https://framerusercontent.com/images/kZBD0dO5DHJnnYTA28CqYvoPE.jpg",
    "https://framerusercontent.com/images/jzZBfSd5pYnek6qcWYGnxt6dH1E.jpg",
    "https://framerusercontent.com/images/zMtJKZOZ8yy0hY1mWqPwJMk9irw.jpg",
]
const labels: Record<Mode, string> = {
    oneoff: "Disconnected one-off activity",
    always: "Connected always-on growth",
    access: "Creator access signal",
    run: "Campaign operations flow",
    learn: "Performance optimisation signal",
    scale: "Compounding growth signal",
}

export default function IRGCardSignal({ mode = "access", style }: Props) {
    const reduced = useReducedMotion()
    const isStatic = useIsStaticRenderer()
    const dark = mode === "always" || mode === "scale"
    const active = reduced || isStatic ? undefined : "active"
    const transition = { duration: reduced ? 0 : 0.42, ease: [0.23, 1, 0.32, 1] as [number, number, number, number] }
    const surface = dark ? "#1F1F1F" : mode === "oneoff" ? "#F4F4F4" : "#FFFFFF"
    const line = dark ? "rgba(255,255,255,.12)" : "rgba(10,10,10,.09)"
    const ink = dark ? "#FFFFFF" : "#0A0A0A"

    const Track = ({ children }: { children: React.ReactNode }) => (
        <div style={{ position: "relative", width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", zIndex: 2 }}>
            <div style={{ position: "absolute", left: 18, right: 18, top: "50%", height: 1, background: line }} />
            <motion.div variants={{ idle: { left: 14, opacity: .55 }, active: { left: "calc(100% - 28px)", opacity: 1 } }} transition={transition} style={{ position: "absolute", top: "calc(50% - 6px)", width: 12, height: 12, borderRadius: 99, background: gradient, boxShadow: "0 4px 18px rgba(34,61,254,.28)", zIndex: 4 }} />
            {children}
        </div>
    )

    const Person = ({ src, i }: { src: string; i: number }) => (
        <motion.div variants={{ idle: { y: 0 }, active: { y: i === 1 ? -6 : -2 } }} transition={transition} style={{ width: i === 1 ? 54 : 44, height: i === 1 ? 54 : 44, borderRadius: 99, overflow: "hidden", border: "4px solid " + surface, boxShadow: "0 8px 24px rgba(0,0,0,.12)", zIndex: 3 }}>
            <img src={src} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </motion.div>
    )

    let visual: React.ReactNode
    if (mode === "access" || mode === "always") {
        visual = <Track>{people.map((src, i) => <Person key={src} src={src} i={i} />)}</Track>
    } else if (mode === "run") {
        visual = <Track>{["Source", "Brief", "Live"].map((text, i) => <motion.div key={text} variants={{ idle: { y: 0 }, active: { y: i === 1 ? -5 : 0 } }} transition={transition} style={{ width: 68, height: 44, borderRadius: 14, background: i === 1 ? gradient : dark ? "#2B2B2B" : "#F4F4F4", color: i === 1 ? "#fff" : ink, display: "grid", placeItems: "center", font: "600 11px/1 'BDO Grotesk', sans-serif", zIndex: 3 }}>{text}</motion.div>)}</Track>
    } else if (mode === "learn") {
        visual = <div style={{ width: "100%", height: 72, display: "flex", alignItems: "end", gap: 12, zIndex: 2 }}>{[46, 62, 78, 58, 88].map((height, i) => <motion.div key={i} variants={{ idle: { height }, active: { height: Math.min(height + (i + 1) * 3, 96) } }} transition={{ ...transition, delay: i * .025 }} style={{ flex: 1, borderRadius: "10px 10px 5px 5px", background: i === 4 ? gradient : dark ? "#333" : "#E9E9E9" }} />)}</div>
    } else if (mode === "scale") {
        visual = <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: 8, zIndex: 2 }}>{["Access", "Performance", "Scale"].map((text, i) => <motion.div key={text} variants={{ idle: { x: i * 10 }, active: { x: i * 20 } }} transition={{ ...transition, delay: i * .03 }} style={{ width: 118 + i * 32, height: 27, borderRadius: 99, background: i === 2 ? gradient : "#303030", color: "#fff", display: "flex", alignItems: "center", paddingLeft: 14, font: "600 10px/1 'BDO Grotesk', sans-serif" }}>{text}</motion.div>)}</div>
    } else {
        const spots = [{ left: "8%", top: "18%" }, { left: "66%", top: "12%" }, { left: "38%", top: "62%" }]
        visual = <div style={{ position: "relative", width: "100%", height: 78, zIndex: 2 }}>{spots.map((spot, i) => <motion.div key={i} variants={{ idle: { x: 0, y: 0 }, active: { x: i === 1 ? 10 : -8, y: i === 2 ? 7 : -4 } }} transition={transition} style={{ position: "absolute", ...spot, width: i === 2 ? 38 : 30, height: i === 2 ? 38 : 30, borderRadius: 99, background: i === 0 ? "#E7E7E7" : i === 1 ? "#DADADA" : gradient, boxShadow: "0 8px 22px rgba(0,0,0,.09)" }} />)}</div>
    }

    return <motion.div
        role="img"
        aria-label={labels[mode]}
        tabIndex={0}
        initial="idle"
        animate="idle"
        whileInView={active}
        viewport={{ once: true, amount: 0.45 }}
        whileHover={active}
        whileFocus={active}
        style={{ ...style, position: "relative", width: "100%", height: "100%", minHeight: 128, borderRadius: 24, overflow: "hidden", background: surface, outline: "none", display: "flex", alignItems: "center", padding: "24px 28px", boxSizing: "border-box" }}
    >
        <div aria-hidden="true" style={{ position: "absolute", inset: 0, opacity: dark ? .18 : .3, backgroundImage: "linear-gradient(" + line + " 1px, transparent 1px), linear-gradient(90deg, " + line + " 1px, transparent 1px)", backgroundSize: "32px 32px" }} />
        {visual}
    </motion.div>
}

addPropertyControls(IRGCardSignal, {
    mode: { type: ControlType.Enum, title: "Signal", options: ["oneoff", "always", "access", "run", "learn", "scale"], optionTitles: ["One-off", "Always-on", "Access", "Run", "Learn", "Scale"], defaultValue: "access" },
})
