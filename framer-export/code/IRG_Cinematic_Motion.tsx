import { forwardRef, useCallback, useEffect, useRef } from "react"
import type { ComponentType, ForwardedRef } from "react"
import { useIsStaticRenderer } from "framer"
import { useReducedMotion, useScroll, useTransform } from "framer-motion"

/**
 * Adds a restrained vertical drift to one editorial media element per page.
 * Touch, static rendering, and reduced-motion users receive the unchanged layer.
 */
export function withSubtleDrift(Component: ComponentType<any>): ComponentType<any> {
    return forwardRef(function IRGSubtleDrift(
        props: any,
        forwardedRef: ForwardedRef<HTMLElement>
    ) {
        const localRef = useRef<HTMLElement | null>(null)
        const isStatic = useIsStaticRenderer()
        const reduceMotion = useReducedMotion()
        const isTouch =
            typeof window !== "undefined" &&
            window.matchMedia("(pointer: coarse)").matches
        const setRef = useCallback(
            (node: HTMLElement | null) => {
                localRef.current = node
                if (typeof forwardedRef === "function") forwardedRef(node)
                else if (forwardedRef) forwardedRef.current = node
            },
            [forwardedRef]
        )
        const { scrollYProgress } = useScroll({
            target: localRef,
            offset: ["start end", "end start"],
        })
        const y = useTransform(scrollYProgress, [0, 1], [-12, 12])
        const motionStyle =
            isStatic || reduceMotion || isTouch
                ? props.style
                : { ...props.style, y }

        return <Component {...props} ref={setRef} style={motionStyle} />
    })
}

/**
 * Rolls the existing editable CTA label on pointer hover and keyboard focus.
 */
export function withLabelRoll(Component: ComponentType<any>): ComponentType<any> {
    return forwardRef(function IRGLabelRoll(
        props: any,
        forwardedRef: ForwardedRef<HTMLElement>
    ) {
        const localRef = useRef<HTMLElement | null>(null)
        const reduceMotion = useReducedMotion()
        const setRef = useCallback(
            (node: HTMLElement | null) => {
                localRef.current = node
                if (typeof forwardedRef === "function") forwardedRef(node)
                else if (forwardedRef) forwardedRef.current = node
            },
            [forwardedRef]
        )

        useEffect(() => {
            if (reduceMotion || typeof document === "undefined") return
            const root = localRef.current
            const label = root?.querySelector<HTMLElement>(
                '[data-framer-component-type="RichTextContainer"]'
            )
            if (!root || !label) return
            root.classList.add("irg-roll-button")
            label.classList.add("irg-roll-label")
            label.dataset.rollLabel = label.textContent || ""
            if (!document.getElementById("irg-roll-motion")) {
                const style = document.createElement("style")
                style.id = "irg-roll-motion"
                style.textContent = ".irg-roll-button{background-size:140% 140%!important;background-position:0 50%;transition:background-position .45s cubic-bezier(.22,1,.36,1)}.irg-roll-button:hover,.irg-roll-button:focus-within{background-position:100% 50%}.irg-roll-button .irg-roll-label{position:relative;display:block;transition:transform .45s cubic-bezier(.22,1,.36,1)}.irg-roll-button .irg-roll-label:after{content:attr(data-roll-label);position:absolute;left:0;top:100%;width:100%;color:inherit;font:inherit;letter-spacing:inherit;white-space:nowrap}.irg-roll-button:hover .irg-roll-label,.irg-roll-button:focus-within .irg-roll-label{transform:translateY(-100%)}@media(prefers-reduced-motion:reduce){.irg-roll-button .irg-roll-label{transition:none!important}.irg-roll-button .irg-roll-label:after{display:none}}"
                document.head.appendChild(style)
            }
            return () => {
                root.classList.remove("irg-roll-button")
                label.classList.remove("irg-roll-label")
                delete label.dataset.rollLabel
            }
        }, [reduceMotion])

        return <Component {...props} ref={setRef} />
    })
}
