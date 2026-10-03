import * as React from "react"
import { addPropertyControls, ControlType, useIsStaticRenderer } from "framer"
import { motion, useReducedMotion } from "framer-motion"

interface FloatingNavShellProps {
    content?: React.ReactNode
    style?: React.CSSProperties
}

/**
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight any-prefer-fixed
 */
export default function FloatingNavShell(props: FloatingNavShellProps) {
    const { content, style } = props
    const isStatic = useIsStaticRenderer()
    const reduceMotion = useReducedMotion()
    const [scrolled, setScrolled] = React.useState(false)

    React.useEffect(() => {
        if (isStatic || typeof window === "undefined") return
        const update = () => setScrolled(window.scrollY > 24)
        update()
        window.addEventListener("scroll", update, { passive: true })
        return () => window.removeEventListener("scroll", update)
    }, [isStatic])

    const active = !isStatic && scrolled

    return (
        <div
            style={{
                ...style,
                position: "relative",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                width: "100%",
                height: "auto",
            }}
        >
            <motion.div
                initial={false}
                animate={{
                    width: active ? "90%" : "100%",
                    backgroundColor: active ? "rgba(255,255,255,.72)" : "rgba(255,255,255,0)",
                    boxShadow: active ? "0 6px 24px rgba(0,0,0,.08)" : "0 0 0 rgba(0,0,0,0)",
                    borderRadius: active ? 999 : 0,
                    backdropFilter: active ? "blur(16px)" : "blur(0px)",
                }}
                transition={{ duration: reduceMotion ? 0 : 0.4, ease: [0.23, 1, 0.32, 1] }}
                style={{
                    position: "relative",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    overflow: "hidden",
                    WebkitBackdropFilter: active ? "blur(16px)" : "blur(0px)",
                }}
            >
                {content}
            </motion.div>
        </div>
    )
}

addPropertyControls(FloatingNavShell, {
    content: {
        type: ControlType.Slot,
        title: "Content",
        maxCount: 1,
    },
})
