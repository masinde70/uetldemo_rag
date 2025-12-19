"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronRight, Check, Circle } from "lucide-react"

// Simple dropdown menu implementation without Radix
// For production, consider using @radix-ui/react-dropdown-menu

interface DropdownMenuProps {
  children: React.ReactNode
}

interface DropdownMenuContextValue {
  open: boolean
  setOpen: (open: boolean) => void
}

const DropdownMenuContext = React.createContext<DropdownMenuContextValue>({
  open: false,
  setOpen: () => {},
})

const DropdownMenu = ({ children }: DropdownMenuProps) => {
  const [open, setOpen] = React.useState(false)
  
  return (
    <DropdownMenuContext.Provider value={{ open, setOpen }}>
      <div className="relative inline-block">
        {children}
      </div>
    </DropdownMenuContext.Provider>
  )
}

const DropdownMenuTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { asChild?: boolean }
>(({ className, children, asChild, ...props }, ref) => {
  const { open, setOpen } = React.useContext(DropdownMenuContext)
  
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    setOpen(!open)
  }
  
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement<any>, {
      onClick: handleClick,
      ref,
    })
  }
  
  return (
    <button
      ref={ref}
      className={className}
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  )
})
DropdownMenuTrigger.displayName = "DropdownMenuTrigger"

interface DropdownMenuContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: "start" | "center" | "end"
  sideOffset?: number
}

const DropdownMenuContent = React.forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  ({ className, align = "center", sideOffset = 4, children, ...props }, ref) => {
    const { open, setOpen } = React.useContext(DropdownMenuContext)
    const contentRef = React.useRef<HTMLDivElement>(null)
    
    // Close on click outside
    React.useEffect(() => {
      if (!open) return
      
      const handleClickOutside = (e: MouseEvent) => {
        if (contentRef.current && !contentRef.current.contains(e.target as Node)) {
          // Check if click is on trigger
          const trigger = contentRef.current.parentElement?.querySelector('[data-dropdown-trigger]')
          if (trigger && trigger.contains(e.target as Node)) return
          setOpen(false)
        }
      }
      
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === "Escape") setOpen(false)
      }
      
      // Use setTimeout to avoid immediate close on same click
      const timeoutId = setTimeout(() => {
        document.addEventListener("mousedown", handleClickOutside)
        document.addEventListener("keydown", handleEscape)
      }, 0)
      
      return () => {
        clearTimeout(timeoutId)
        document.removeEventListener("mousedown", handleClickOutside)
        document.removeEventListener("keydown", handleEscape)
      }
    }, [open, setOpen])
    
    if (!open) return null
    
    return (
      <div
        ref={contentRef}
        className={cn(
          "absolute z-[100] min-w-[8rem] overflow-hidden rounded-md border border-border-default bg-bg-surface-1 p-1 shadow-lg",
          "animate-in fade-in-0 zoom-in-95",
          align === "end" && "right-0",
          align === "start" && "left-0",
          align === "center" && "left-1/2 -translate-x-1/2",
          className
        )}
        style={{ top: `calc(100% + ${sideOffset}px)` }}
        {...props}
      >
        {children}
      </div>
    )
  }
)
DropdownMenuContent.displayName = "DropdownMenuContent"

const DropdownMenuItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { 
    asChild?: boolean
    inset?: boolean 
  }
>(({ className, asChild, inset, children, ...props }, ref) => {
  const { setOpen } = React.useContext(DropdownMenuContext)
  
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    props.onClick?.(e)
    setOpen(false)
  }
  
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement<any>, {
      className: cn(
        "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-bg-surface-2 hover:text-text-primary focus:bg-bg-surface-2 focus:text-text-primary",
        inset && "pl-8",
        className
      ),
      onClick: handleClick,
      ref,
    })
  }
  
  return (
    <div
      ref={ref}
      className={cn(
        "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-bg-surface-2 hover:text-text-primary focus:bg-bg-surface-2 focus:text-text-primary",
        inset && "pl-8",
        className
      )}
      onClick={handleClick}
      {...props}
    >
      {children}
    </div>
  )
})
DropdownMenuItem.displayName = "DropdownMenuItem"

const DropdownMenuLabel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { inset?: boolean }
>(({ className, inset, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "px-2 py-1.5 text-sm font-semibold text-text-primary",
      inset && "pl-8",
      className
    )}
    {...props}
  />
))
DropdownMenuLabel.displayName = "DropdownMenuLabel"

const DropdownMenuSeparator = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("-mx-1 my-1 h-px bg-border-default", className)}
    {...props}
  />
))
DropdownMenuSeparator.displayName = "DropdownMenuSeparator"

const DropdownMenuShortcut = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement>) => {
  return (
    <span
      className={cn("ml-auto text-xs tracking-widest text-text-tertiary", className)}
      {...props}
    />
  )
}
DropdownMenuShortcut.displayName = "DropdownMenuShortcut"

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
}
