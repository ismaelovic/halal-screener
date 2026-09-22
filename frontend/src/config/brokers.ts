export interface BrokerCTAConfig {
  name: string;
  blurb: string;
  url: string;
}

// Placeholder links only — no real affiliate tracking params wired up yet.
// Swap these for real affiliate URLs once accounts are approved (Adtraction, etc).
export const BROKER_CTAS: BrokerCTAConfig[] = [
  {
    name: "Nordnet",
    blurb: "Popular Nordic broker with a wide selection of European stocks.",
    url: "https://www.nordnet.dk",
  },
  {
    name: "Saxo",
    blurb: "Danish broker offering global market access.",
    url: "https://www.home.saxo",
  },
];
