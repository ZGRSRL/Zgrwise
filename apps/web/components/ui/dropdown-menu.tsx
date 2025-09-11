import * as React from "react"
import { cn, PolymorphicProps, filterAsChildProps } from "@/lib/utils"

const DropdownMenu = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("relative inline-block text-left", className)}
    {...props}
  />
))
DropdownMenu.displayName = "DropdownMenu"

type DropdownMenuTriggerBaseProps = {
  asChild?: boolean;
};

type DropdownMenuTriggerProps<C extends React.ElementType = "button"> = 
  PolymorphicProps<C, DropdownMenuTriggerBaseProps>;

const DropdownMenuTrigger = React.forwardRef<
  HTMLButtonElement,
  DropdownMenuTriggerProps
>(function DropdownMenuTrigger<C extends React.ElementType = "button">(
  props: DropdownMenuTriggerProps<C>,
  ref: React.Ref<HTMLButtonElement>
) {
  const {
    as,
    asChild,
    className,
    children,
    ...rest
  } = props as DropdownMenuTriggerProps;

  const classes = cn("inline-flex items-center justify-center", className);

  // asChild: çocuk elemente *filtrelenmiş* prop'lar aktarılır
  if (asChild && React.isValidElement(children)) {
    const filtered = filterAsChildProps(rest);
    return React.cloneElement(children as React.ReactElement, {
      ...filtered,
      className: cn((children as any).props?.className, classes),
      ref
    });
  }

  // polymorphic: <button> varsayılan, istenirse as ile <a>, <div> vs.
  const Comp = (as || "button") as React.ElementType;
  return (
    <Comp ref={ref as any} className={classes} {...(rest as any)}>
      {children}
    </Comp>
  );
})
DropdownMenuTrigger.displayName = "DropdownMenuTrigger"

const DropdownMenuContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { align?: "start" | "end" }
>(({ className, align = "start", ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "absolute z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
      align === "end" ? "right-0" : "left-0",
      "top-full mt-1",
      className
    )}
    {...props}
  />
))
DropdownMenuContent.displayName = "DropdownMenuContent"

const DropdownMenuItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground",
      className
    )}
    {...props}
  />
))
DropdownMenuItem.displayName = "DropdownMenuItem"

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
}