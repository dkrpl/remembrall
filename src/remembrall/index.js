// Root entrypoint for Node-based agent plugin registrations and programmatic API.
export * from "./engine.js";

export const name = "remembrall";
export const version = "1.0.0";
export default {
  name,
  version,
  skills: ["./skills/remembrall"]
};
