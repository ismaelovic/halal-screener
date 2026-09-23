export interface PopularTicker {
  ticker: string;
  exchange: string;
  name: string;
  subtitle: string;
}

export const POPULAR_TICKERS: PopularTicker[] = [
  { ticker: "NOVO-B", exchange: "CO", name: "Novo Nordisk", subtitle: "Healthcare" },
  { ticker: "ASML", exchange: "AS", name: "ASML Holding", subtitle: "Semiconductors" },
  { ticker: "MAERSK-B", exchange: "CO", name: "Maersk", subtitle: "Shipping" },
  { ticker: "SAP", exchange: "DE", name: "SAP", subtitle: "Software" },
  { ticker: "DGE", exchange: "L", name: "Diageo", subtitle: "Beverages" },
  { ticker: "DANSKE", exchange: "CO", name: "Danske Bank", subtitle: "Banking" },
  { ticker: "AAPL", exchange: "US", name: "Apple", subtitle: "Technology" },
  { ticker: "PM", exchange: "US", name: "Philip Morris", subtitle: "Tobacco" },
];

export const POPULAR_CARD_GRADIENTS: [string, string][] = [
  ["#5B6CFF", "#8A4FFF"],
  ["#FF7A5B", "#FF4F8A"],
  ["#22C1C3", "#0F8B8D"],
  ["#F7B733", "#FC4A1A"],
];
