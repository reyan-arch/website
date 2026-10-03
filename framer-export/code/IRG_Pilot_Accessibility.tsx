import { forwardRef, type ComponentType } from "react"

const styles = `@media (prefers-reduced-motion: reduce) { :is(#services, #services-pilot-specimen) [style*="will-change"] { opacity: 1 !important; transform: none !important; animation: none !important; transition: none !important; will-change: auto !important; } }`

export function withPilotAccessibility(Component: ComponentType<any>): ComponentType {
 return forwardRef(function PilotAccessibility(props, ref) {
  return <><style>{styles}</style><Component {...props} ref={ref} /></>
 })
}
