import React, { useEffect, useRef, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { T } from "./Bilingual.jsx";
import LanguageToggle from "./LanguageToggle.jsx";

// Each section has its own color (see .main-nav in index.css).
const NAV = [
  { to: "/", key: "navHome", icon: "🏠", hue: 265 },
  { to: "/translate", key: "navTranslate", icon: "🤟", hue: 170 },
  { to: "/teach", key: "navTeach", icon: "🎓", hue: 38 },
  { to: "/conversation", key: "navConversation", icon: "💬", hue: 330 },
  { to: "/vocabulary", key: "navVocabulary", icon: "📚", hue: 200 },
];

const ALWAYS_SHOW_NEAR_TOP_PX = 80;
const SCROLL_THRESHOLD_PX = 8;

/**
 * Fixed header. The brand bar always stays in view; the menu slides up out of the
 * way while scrolling down and slides back when scrolling up or near the top.
 * A spacer keeps page content from starting underneath the header, and
 * --header-visible tells sticky elements (e.g. the conversation panel) how much
 * of the screen the header currently covers.
 */
export default function SiteHeader() {
  const { pathname } = useLocation();
  const topbarRef = useRef(null);
  const navRef = useRef(null);
  const [navHidden, setNavHidden] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [heights, setHeights] = useState({ topbar: 0, nav: 0 });

  useEffect(() => {
    let lastY = window.scrollY;
    let frame = 0;
    const update = () => {
      frame = 0;
      const y = window.scrollY;
      setScrolled(y > 4);
      if (y < ALWAYS_SHOW_NEAR_TOP_PX) {
        setNavHidden(false);
        lastY = y;
        return;
      }
      if (Math.abs(y - lastY) < SCROLL_THRESHOLD_PX) return;
      setNavHidden(y > lastY);
      lastY = y;
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(frame);
    };
  }, []);

  // A new page starts at the top, with the menu visible.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  useEffect(() => {
    const observer = new ResizeObserver(() => {
      setHeights({ topbar: topbarRef.current.offsetHeight, nav: navRef.current.offsetHeight });
    });
    observer.observe(topbarRef.current);
    observer.observe(navRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const visible = heights.topbar + (navHidden ? 0 : heights.nav);
    document.documentElement.style.setProperty("--header-visible", `${visible}px`);
  }, [heights, navHidden]);

  return (
    <>
      <header className={`site-header${navHidden ? " nav-hidden" : ""}${scrolled ? " scrolled" : ""}`}>
        <div className="topbar" ref={topbarRef}>
          <div className="brand">
            {/* same artwork as the browser tab icon */}
            <img className="logo" src={`${import.meta.env.BASE_URL}favicon.svg`} alt="" />
            <div>
              <h1>SignBridge</h1>
              <div className="tagline">
                <T k="tagline" />
              </div>
            </div>
          </div>
          <LanguageToggle />
        </div>

        <nav className="main-nav" ref={navRef} inert={navHidden}>
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"} style={{ "--hue": item.hue }}>
              <span className="nav-icon">{item.icon}</span>
              <T k={item.key} />
            </NavLink>
          ))}
        </nav>
      </header>
      <div className="header-spacer" style={{ height: heights.topbar + heights.nav }} />
    </>
  );
}
