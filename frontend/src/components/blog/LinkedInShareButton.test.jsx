import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import LinkedInShareButton from "./LinkedInShareButton";

describe("LinkedInShareButton", () => {
  const originalLocation = window.location;

  beforeEach(() => {
    delete window.location;
    window.location = {
      ...originalLocation,
      origin: "https://blog.example.com",
      pathname: "/articles/mon-titre",
    };
  });

  afterEach(() => {
    window.location = originalLocation;
  });

  it("renders nothing when status is not 'published'", () => {
    const { container } = render(
      <LinkedInShareButton title="Mon titre" status="draft" />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("renders the share link when status is 'published'", () => {
    render(<LinkedInShareButton title="Mon titre" status="published" />);
    expect(
      screen.getByRole("link", { name: /partager .* sur linkedin/i }),
    ).toBeInTheDocument();
  });

  it("builds the share URL from window.location.origin + pathname", () => {
    render(<LinkedInShareButton title="Mon titre" status="published" />);
    const link = screen.getByRole("link", { name: /partager .* sur linkedin/i });

    const expectedTarget = encodeURIComponent(
      "https://blog.example.com/articles/mon-titre",
    );
    expect(link).toHaveAttribute(
      "href",
      `https://www.linkedin.com/sharing/share-offsite/?url=${expectedTarget}`,
    );
  });

  it("includes the title in the aria-label", () => {
    render(
      <LinkedInShareButton title="Article génial" status="published" />,
    );
    const link = screen.getByRole("link", { name: /partager .* sur linkedin/i });
    expect(link).toHaveAttribute(
      "aria-label",
      "Partager « Article génial » sur LinkedIn",
    );
  });

  it("opens the link in a new tab with safe rel attributes", () => {
    render(<LinkedInShareButton title="Mon titre" status="published" />);
    const link = screen.getByRole("link", { name: /partager .* sur linkedin/i });
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });
});
