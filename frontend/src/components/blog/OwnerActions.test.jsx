import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import OwnerActions from "./OwnerActions";

const renderWithRouter = (ui) =>
  render(<MemoryRouter>{ui}</MemoryRouter>);

const basePost = {
  slug: "mon-article",
  status: "published",
  is_owner: true,
  is_pinned: false,
  has_draft: false,
};

const baseProps = {
  publishing: false,
  onPublish: () => {},
  pinToggling: false,
  onTogglePin: () => {},
  hasVersions: false,
  hasDraftChanges: false,
};

describe("OwnerActions", () => {
  it("renders nothing when the user is anonymous", () => {
    const { container } = renderWithRouter(
      <OwnerActions post={basePost} user={null} {...baseProps} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing when the user is the owner but not a superuser", () => {
    const { container } = renderWithRouter(
      <OwnerActions
        post={basePost}
        user={{ is_superuser: false }}
        {...baseProps}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing when the user is a superuser but not the owner", () => {
    const { container } = renderWithRouter(
      <OwnerActions
        post={{ ...basePost, is_owner: false }}
        user={{ is_superuser: true }}
        {...baseProps}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("renders the toolbar for a superuser owner with the expected actions", () => {
    renderWithRouter(
      <OwnerActions
        post={basePost}
        user={{ is_superuser: true }}
        {...baseProps}
      />,
    );

    expect(screen.getByTestId("owner-actions")).toBeInTheDocument();
    expect(screen.getByText("Auteur")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /modifier/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /supprimer/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /épingler/i })).toBeInTheDocument();
  });

  it("shows the unpublished-changes hint when hasDraftChanges is true", () => {
    renderWithRouter(
      <OwnerActions
        post={basePost}
        user={{ is_superuser: true }}
        {...baseProps}
        hasDraftChanges
      />,
    );

    expect(
      screen.getByText("Modifications non publiées"),
    ).toBeInTheDocument();
  });

  it("uses the responsive sticky utility classes (md+ only)", () => {
    renderWithRouter(
      <OwnerActions
        post={basePost}
        user={{ is_superuser: true }}
        {...baseProps}
      />,
    );

    const bar = screen.getByTestId("owner-actions");
    expect(bar.className).toContain("md:sticky");
    expect(bar.className).toContain("md:top-[var(--header-height)]");
    expect(bar.className).toContain("md:z-[var(--z-owner-actions)]");
  });
});
