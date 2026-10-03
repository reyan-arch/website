import * as React from "react"
import type { ComponentType } from "react"
import { useReducedMotion } from "framer-motion"

export function withFloatingNav(Component: ComponentType<any>): ComponentType<any> {
    return React.forwardRef(function FloatingNavOverride(props, ref) {
        const [scrolled, setScrolled] = React.useState(false)
        const reduceMotion = useReducedMotion()
        const navRef = React.useRef<HTMLElement | null>(null)
        const setRef = React.useCallback((node: HTMLElement | null) => {
            navRef.current = node
            if (typeof ref === "function") ref(node)
            else if (ref) (ref as React.MutableRefObject<HTMLElement | null>).current = node
        }, [ref])

        React.useLayoutEffect(() => {
            const update = () => setScrolled(window.scrollY > 24)
            update()
            window.addEventListener("scroll", update, { passive: true })
            window.addEventListener("pageshow", update)
            return () => {
                window.removeEventListener("scroll", update)
                window.removeEventListener("pageshow", update)
            }
        }, [])

        React.useEffect(() => {
            const nav = navRef.current
            if (!nav) return
            const syncButton = () => {
                const button = nav.querySelector<HTMLButtonElement>("button")
                if (!button) return
                const open = button.dataset.framerName === "Close navigation"
                button.type = "button"
                button.setAttribute("aria-label", open ? "Close menu" : "Open menu")
                button.setAttribute("aria-expanded", String(open))
            }
            syncButton()
            const observer = new MutationObserver(syncButton)
            observer.observe(nav, { childList: true, subtree: true, attributes: true, attributeFilter: ["data-framer-name"] })
            const close = (restoreFocus = false) => {
                const button = nav.querySelector<HTMLButtonElement>('[data-framer-name="Close navigation"]')
                if (!button) return
                button.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true, pointerId: 1, pointerType: "mouse", isPrimary: true, button: 0 }))
                button.dispatchEvent(new PointerEvent("pointerup", { bubbles: true, pointerId: 1, pointerType: "mouse", isPrimary: true, button: 0 }))
                if (restoreFocus) requestAnimationFrame(() => nav.querySelector<HTMLButtonElement>('[data-framer-name="Open navigation"]')?.focus())
            }
            const key = (event: KeyboardEvent) => {
                if (event.key === "Escape" && nav.querySelector('[data-framer-name="Close navigation"]')) {
                    event.preventDefault()
                    close(true)
                }
            }
            const outside = (event: Event) => { if (!nav.contains(event.target as Node)) close() }
            const navigate = (event: MouseEvent) => { if ((event.target as Element).closest("a[href]")) close() }
            const resize = () => close()
            document.addEventListener("keydown", key)
            document.addEventListener("pointerdown", outside)
            document.addEventListener("focusin", outside)
            nav.addEventListener("click", navigate)
            window.addEventListener("popstate", resize)
            window.addEventListener("resize", resize)
            return () => {
                observer.disconnect()
                document.removeEventListener("keydown", key)
                document.removeEventListener("pointerdown", outside)
                document.removeEventListener("focusin", outside)
                nav.removeEventListener("click", navigate)
                window.removeEventListener("popstate", resize)
                window.removeEventListener("resize", resize)
            }
        }, [])

        return (
            <>
            <style>{`
/* Holafly CMS sections share the existing fields. Keep the documented block order in Results. */
[data-framer-name="holafly_headline"] h1::first-line { font-size: 2.7em; line-height: 1; letter-spacing: -.06em; }
[data-framer-name="holafly_headline"] h1 { font-size: clamp(42px,4.4vw,76px)!important; line-height:1.06!important; text-wrap:initial!important; }
[data-framer-name="holafly_vineyard"] > :nth-child(n+3),
[data-framer-name="holafly_obayd"] > :not(:nth-child(3)):not(:nth-child(4)):not(:nth-child(5)),
[data-framer-name="holafly_ben"] > :not(:nth-child(6)):not(:nth-child(7)):not(:nth-child(8)),
[data-framer-name="holafly_results_copy"] > :nth-child(-n+9),
[data-framer-name="holafly_markets"] > :not(:last-child),
[data-framer-name="holafly_challenge"] > :nth-last-child(-n+2),
[data-framer-name="holafly_sequence"] > :not(blockquote),
[data-framer-name="holafly_changes"] > blockquote { display:none!important; }
[data-framer-name="holafly_vineyard"] > * { color:#fff!important; margin-top:0!important; font-size:14px!important; line-height:1.5!important; }
[data-framer-name="holafly_obayd"] > h2,
[data-framer-name="holafly_ben"] > h2 { font-size:20px!important; line-height:1.3!important; margin-top:0!important; margin-bottom:20px!important; }
[data-framer-name="holafly_obayd"] > h3 { font-size:clamp(48px,6vw,88px)!important; line-height:1.04!important; letter-spacing:-.045em!important; margin-top:0!important; margin-bottom:24px!important; }
[data-framer-name="holafly_ben"] > h3 { font-size:clamp(34px,4vw,56px)!important; line-height:1.1!important; margin-top:0!important; margin-bottom:24px!important; }
[data-framer-name="holafly_markets"] > p { margin-top:0!important; }
[data-framer-name="holafly_challenge"] > h3 { font-size:clamp(30px,3.6vw,48px)!important; line-height:1.12!important; margin-bottom:28px!important; }
[data-framer-name="holafly_changes"] > h3 { margin-top:32px!important; margin-bottom:10px!important; font-size:24px!important; }
[data-framer-name="holafly_changes"] > h3:first-child { margin-top:0!important; }
[data-framer-name="holafly_sequence"] blockquote { border:0!important; padding:0!important; margin:0!important; }
[data-framer-name="holafly_sequence"] blockquote p { font-size:28px!important; line-height:1.6!important; font-weight:500!important; }
[data-framer-name="holafly_results_copy"] :is(p,h2,h3,th,td) { color:#fff!important; }
[data-framer-name="holafly_results_copy"] > p { max-width:760px; }
[data-framer-name="holafly_results_copy"] > p:nth-child(10) { margin-top:0!important; }
[data-framer-name="holafly_results_copy"] > h2 { font-size:clamp(28px,3vw,42px)!important; margin-top:64px!important; margin-bottom:28px!important; }
[data-framer-name="holafly_results_copy"] table { width:100%!important; border-collapse:collapse!important; table-layout:fixed!important; background:transparent!important; }
[data-framer-name="holafly_results_copy"] :is(th,td) { text-align:left!important; vertical-align:top!important; padding:24px 16px!important; border:0!important; border-bottom:1px solid #4b5054!important; background:transparent!important; }
[data-framer-name="holafly_results_copy"] :is(th,td) p { font-size:17px!important; }
[data-framer-name="holafly_results_copy"] > p:last-child { font-size:14px!important; color:#c3c7cb!important; margin-top:24px!important; }
@media(max-width:1199px) {
 [data-framer-name="holafly_headline"] h1 { font-size:52px!important; max-width:520px; }
 [data-framer-name="holafly_headline"] h1::first-line { font-size:2.55em; }
}
@media(max-width:599px) {
 [data-framer-name="holafly_headline"] h1 { font-size:38px!important; }
 [data-framer-name="holafly_headline"] h1::first-line { font-size:2.6em; }
 [data-framer-name="holafly_changes"] > h3 { font-size:22px!important; }
 [data-framer-name="holafly_results_copy"] table,
 [data-framer-name="holafly_results_copy"] tbody { display:block!important; }
 [data-framer-name="holafly_results_copy"] thead { position:absolute!important; width:1px!important; height:1px!important; overflow:hidden!important; clip-path:inset(50%); }
 [data-framer-name="holafly_results_copy"] tr { display:grid!important; grid-template-columns:1fr!important; padding:24px 0!important; border-bottom:1px solid #4b5054!important; }
 [data-framer-name="holafly_results_copy"] tr:has(>th:nth-child(2)) { position:absolute!important; width:1px!important; height:1px!important; overflow:hidden!important; clip-path:inset(50%); }
 [data-framer-name="holafly_results_copy"] :is(th,td) { display:block!important; width:100%!important; border:0!important; padding:6px 0!important; }
 [data-framer-name="holafly_results_copy"] tr>th p { font-size:24px!important; }
 [data-framer-name="holafly_results_copy"] td::before { color:#c3c7cb; font:14px/1.4 "BDO Grotesk Variable",sans-serif; }
 [data-framer-name="holafly_results_copy"] td:nth-child(2)::before { content:"Organic views"; }
 [data-framer-name="holafly_results_copy"] td:nth-child(3)::before { content:"Against view target"; }
 [data-framer-name="holafly_results_copy"] td:nth-child(4)::before { content:"Cost below plan"; }
}

[data-framer-name="holafly_sequence"] blockquote p { padding:16px 0; margin:0!important; border-bottom:1px solid #ccd0d2; }
[data-framer-name="holafly_sequence"] blockquote p:not(:last-child)::after { content:"→"; float:right; color:#697078; }
[data-framer-name="holafly_sequence"] blockquote p:first-child { color:#d92b36!important; }
[data-framer-name="holafly_sequence"] blockquote p:last-child { color:#3439c8!important; border:0; }

                nav { --irg-nav-ink: #1F1F1F; }
                body:has([data-framer-name="IRG opening dark"]) nav {
                    --irg-nav-ink: #FFFFFF;
                }
                nav[data-irg-scrolled="true"] { --irg-nav-ink: #1F1F1F !important; }
                nav [data-framer-name="Navigation Links"] :is(a, .framer-text),
                nav [data-framer-name="IRG Logo"] .framer-text {
                    color: var(--irg-nav-ink, #1F1F1F) !important;
                    mix-blend-mode: normal !important;
                }
                :is(a[href], button, input, textarea, select, [tabindex]):focus-visible {
                    outline: 2px solid #FFFFFF !important;
                    outline-offset: 3px !important;
                    box-shadow: 0 0 0 5px #1F1F1F !important;
                }
                nav:has([data-framer-name="Close navigation"]) {
                    --irg-nav-ink: #1F1F1F !important;
                    background: #FFFFFF !important;
                    border-radius: 24px !important;
                    box-shadow: 0 12px 36px rgba(0,0,0,.12) !important;
                }
                nav [data-framer-name="Menu line"] { background: var(--irg-nav-ink) !important; }
                nav [data-framer-name="Close navigation"] [data-framer-name="Menu line"]:first-child { transform: translateY(4px) rotate(45deg) !important; }
                nav [data-framer-name="Close navigation"] [data-framer-name="Menu line"]:last-child { transform: translateY(-4px) rotate(-45deg) !important; }
                nav button { border: 0; appearance: none; }
                @media (max-width: 1199px) {
                    nav { width: 100% !important; height: auto !important; border-radius: 24px !important; max-height: calc(100dvh - 40px); overflow-y: auto !important; }
                    nav [data-framer-name="Navigation Links"] a {
                        display: flex; align-items: center; justify-content: flex-start;
                        min-height: 48px; width: 100%; font-size: 22px !important;
                    }
                    nav [data-framer-name="Navigation Links"] { grid-column: 1 / -1; }
                    nav [data-framer-name="Navigation Actions"] { grid-column: 1 / -1; padding-bottom: 12px; }
                    nav [data-framer-name="IRG Logo"] { min-height: 44px; }
                }
                @media (prefers-reduced-motion: reduce) {
                    nav, nav * { transition: none !important; animation: none !important; }
                }
            `}</style>
            <Component
                {...props}
                ref={setRef}
                data-irg-scrolled={scrolled ? "true" : "false"}
                style={{
                    ...props.style,
                    width: scrolled ? "90%" : "100%",
                    margin: "0 auto",
                    backgroundColor: scrolled ? "rgba(255,255,255,.94)" : "transparent",
                    backdropFilter: scrolled ? "blur(16px)" : "blur(0px)",
                    WebkitBackdropFilter: scrolled ? "blur(16px)" : "blur(0px)",
                    boxShadow: scrolled ? "0 6px 24px rgba(0,0,0,.08)" : "none",
                    borderRadius: 999,
                    isolation: "isolate",
                    transition: reduceMotion ? "none" : "width .4s cubic-bezier(.22,1,.36,1), background-color .2s, box-shadow .2s",
                }}
            />
            </>
        )
    })
}

// Keep Framer's native player and poster; respect the visitor's motion preference.
export function withVideoMotion(Component: ComponentType<any>): ComponentType<any> {
    return React.forwardRef(function VideoMotion(props, ref) {
        const reduceMotion = useReducedMotion()
        return <Component {...props} ref={ref} playing={reduceMotion ? false : props.playing} />
    })
}

export function withQuestionState(Component: ComponentType<any>): ComponentType<any> {
    return React.forwardRef((props, ref) => <Component {...props} ref={ref} aria-expanded={props["data-framer-name"] === "Question expanded"} />)
}

