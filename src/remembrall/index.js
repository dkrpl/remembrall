// Root entrypoint for Node-based agent plugin registrations.
export const name = "remembrall";
export const version = "1.0.0";
export default {
  name,
  version,
  skills: ["./skills/remembrall"]
};
