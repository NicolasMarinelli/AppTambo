import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    watch: {
      // Docker Desktop on Windows doesn't reliably forward native filesystem
      // events through the bind mount, so chokidar's default watcher misses
      // edits made from the host. Polling works around that.
      usePolling: true,
      interval: 300,
    },
  },
});
