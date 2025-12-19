"use client";

import React from "react";
import { motion } from "framer-motion";
import { useTheme } from "next-themes";

export const MeshBackground: React.FC = () => {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Prevent hydration mismatch
  if (!mounted) {
    return <div className="fixed inset-0 -z-10 bg-background" />;
  }

  const isDark = resolvedTheme === "dark";

  return (
    <div
      className={`fixed inset-0 -z-10 overflow-hidden pointer-events-none transition-colors duration-500 ${
        isDark
          ? "bg-bg-primary"
          : "bg-gradient-to-br from-white via-slate-50 to-blue-50"
      }`}
    >
      {/* Animated Orbs - Only in dark mode */}
      {isDark && (
        <>
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              x: [0, 100, 0],
              y: [0, 50, 0],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "linear",
            }}
            className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] rounded-full bg-neon-cyan/20 blur-[100px]"
          />
          <motion.div
            animate={{
              scale: [1.2, 1, 1.2],
              x: [0, -100, 0],
              y: [0, -50, 0],
            }}
            transition={{
              duration: 25,
              repeat: Infinity,
              ease: "linear",
            }}
            className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full bg-neon-violet/20 blur-[100px]"
          />
          <motion.div
            animate={{
              opacity: [0.3, 0.6, 0.3],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 15,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="absolute top-[20%] right-[10%] w-[40%] h-[40%] rounded-full bg-blue-500/15 blur-[80px]"
          />
        </>
      )}

      {/* Subtle accent for light mode */}
      {!isDark && (
        <>
          <div className="absolute top-0 right-0 w-[50%] h-[50%] rounded-full bg-primary/5 blur-[100px]" />
          <div className="absolute bottom-0 left-0 w-[40%] h-[40%] rounded-full bg-accent/5 blur-[80px]" />
        </>
      )}

      {/* Noise Texture Overlay */}
      <div
        className={`absolute inset-0 mix-blend-overlay pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] ${
          isDark ? "opacity-[0.02]" : "opacity-[0.03]"
        }`}
      />
    </div>
  );
};
