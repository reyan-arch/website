import { useEffect, useRef, useState, useId, type CSSProperties } from "react"
import { useIsStaticRenderer } from "framer"

interface Props { style?: CSSProperties }
const images = [
  {
    "small": "https://framerusercontent.com/images/VeJIb5pX5XZPoCVRmgNiMogPE9U.webp",
    "large": "https://framerusercontent.com/images/ZU4cw1ixHggQotHW2rUkklBshgY.webp"
  },
  {
    "small": "https://framerusercontent.com/images/o66TRJdRERRPVpZKL1ODj0nZxo.webp",
    "large": "https://framerusercontent.com/images/WqjuV5Y5bsRBVryCED5W85avI0E.webp"
  },
  {
    "small": "https://framerusercontent.com/images/8ZPcmShSeCEU6jC7DUzQlaaKuLs.webp",
    "large": "https://framerusercontent.com/images/8llRJ5hGZenjNkSLmR5swQWdB0.webp"
  },
  {
    "small": "https://framerusercontent.com/images/bftBjEaR8glaOMub8IYzHHfZ2gc.webp",
    "large": "https://framerusercontent.com/images/8GYjo4X224kJ5R5CoBy54Qo.webp"
  },
  {
    "small": "https://framerusercontent.com/images/jrN2tKsbqDfNHYIP8Wpm0zLah4.webp",
    "large": "https://framerusercontent.com/images/2k6nDxmNOz4OTwdfJxykjiCbpH0.webp"
  },
  {
    "small": "https://framerusercontent.com/images/Yer37v6oP9fkF6cb6ZXeM3cIc.webp",
    "large": "https://framerusercontent.com/images/oNrPR75B7qjIiBBOg7Dqczt0.webp"
  }
]
const rows = [images, [images[3],images[5],images[1],images[4],images[0],images[2]], [images[2],images[0],images[4],images[1],images[5],images[3]]]
const css = "[data-irg-media-wall] .title{text-wrap:balance}@keyframes irg-wall-left{to{transform:translateX(calc(-50% - 9px))}}@keyframes irg-wall-right{from{transform:translateX(calc(-50% - 9px))}to{transform:translateX(0)}}@media(prefers-reduced-motion:reduce){[data-irg-media-wall] .track{animation:none!important;transform:translateX(-18%)!important}}@media(max-width:810px){[data-irg-media-wall] .copy{padding:32px!important}[data-irg-media-wall] .title{font-size:40px!important}[data-irg-media-wall] .body{font-size:16px!important;line-height:24px!important}}@media(max-width:540px){[data-irg-media-wall] .rail{width:170%!important;left:-35%!important;height:160px!important;transform:rotate(-9deg)!important}[data-irg-media-wall] .r0{top:-24px!important}[data-irg-media-wall] .r1{top:174px!important}[data-irg-media-wall] .r2{top:372px!important}[data-irg-media-wall] .card{width:220px!important;border-radius:18px!important}[data-irg-media-wall] .copy{width:calc(100% - 40px)!important;padding:24px 20px!important;border-radius:24px!important}[data-irg-media-wall] .title{font-size:34px!important;letter-spacing:0!important}[data-irg-media-wall] .body{font-size:15px!important;line-height:22px!important}}"

/** @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight any-prefer-fixed */
export default function IRGMasonryTicker(props: Props) {
  const isStatic = useIsStaticRenderer()
  const titleId = useId()
  const root = useRef<HTMLElement>(null)
  const [near, setNear] = useState(false)
  const [visible, setVisible] = useState(false)
  const [hidden, setHidden] = useState(false)
  useEffect(() => {
    if (isStatic || !root.current) return
    const warm = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) { setNear(true); warm.disconnect() }
    }, { rootMargin: "1000px" })
    const viewport = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting))
    warm.observe(root.current)
    viewport.observe(root.current)
    const visibility = () => setHidden(document.hidden)
    visibility()
    document.addEventListener("visibilitychange", visibility)
    return () => { warm.disconnect(); viewport.disconnect(); document.removeEventListener("visibilitychange", visibility) }
  }, [isStatic])
  return <section ref={root} data-irg-media-wall="true" aria-labelledby={titleId} style={{...props.style,position:"relative",width:"100%",height:"100%",minHeight:620,overflow:"hidden",background:"#0A0A0A",isolation:"isolate"}}>
    <style>{css}</style>
    {rows.map((items,row)=><div className={"rail r"+row} key={row} aria-hidden="true" style={{position:"absolute",top:[-70,190,450][row],left:"-15%",width:"130%",height:214,overflow:"hidden",transform:"rotate(-7deg)",pointerEvents:"none"}}>
      <div className="track" style={{display:"flex",width:"max-content",height:"100%",gap:18,animation:isStatic?"none":(row===1?"irg-wall-right 46s linear infinite":"irg-wall-left 42s linear infinite"),animationPlayState:visible && !hidden ? "running" : "paused",willChange:visible && !hidden ? "transform" : "auto",transform:isStatic?"translateX(-12%)":undefined}}>
        {[...items,...items].map((src,i)=><figure className="card" key={src.small+i} style={{position:"relative",width:"clamp(260px,28vw,430px)",height:"100%",margin:0,overflow:"hidden",flex:"0 0 auto",borderRadius:24,background:"#1F1F1F"}}><picture><source media="(max-width: 540px)" srcSet={src.small}/><img src={src.small} srcSet={`${src.small} 480w, ${src.large} 960w`} sizes="(max-width: 540px) 220px, (max-width: 928px) 260px, (max-width: 1535px) 28vw, 430px" alt="" loading={near || isStatic ? "eager" : "lazy"} decoding="async" onError={event => { event.currentTarget.style.visibility = "hidden" }} style={{width:"100%",height:"100%",objectFit:"cover",display:"block"}}/></picture><div style={{position:"absolute",inset:0,background:"rgba(10,10,10,.16)"}}/></figure>)}
      </div>
    </div>)}
    <div style={{position:"absolute",inset:0,zIndex:1,background:"radial-gradient(circle at center,rgba(10,10,10,.12) 0%,rgba(10,10,10,.54) 68%,rgba(10,10,10,.76) 100%)"}}/>
    <div className="copy" style={{position:"absolute",zIndex:2,left:"50%",top:"50%",transform:"translate(-50%,-50%)",width:"min(840px,calc(100% - 48px))",padding:"42px 48px",borderRadius:32,background:"rgba(10,10,10,.86)",boxShadow:"0 24px 70px rgba(0,0,0,.28)",textAlign:"center"}}>
      <div style={{width:56,height:4,margin:"0 auto 20px",borderRadius:99,background:"linear-gradient(135deg,#FF3131 0%,#223DFE 100%)"}}/>
      <div style={{color:"rgba(255,255,255,.72)",fontFamily:"'BDO Grotesk Variable', sans-serif",fontSize:14,fontWeight:600,lineHeight:1.2,marginBottom:16}}>Creator-led formats</div>
      <h2 id={titleId} className="title" style={{margin:0,color:"#FFFFFF",fontFamily:"'BDO Grotesk Variable', sans-serif",fontSize:52,fontWeight:600,lineHeight:1.05,letterSpacing:"-0.02em"}}>Built for how travel, hospitality and lifestyle are discovered.</h2>
    </div>
  </section>
}
