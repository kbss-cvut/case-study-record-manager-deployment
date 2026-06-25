"use strict";

const elements = {
    servicesGrid: document.getElementById("servicesGrid")
};

async function loadServices() {
    const response = await fetch("./services.json", {
        method: "GET",
        cache: "no-store",
        headers: {
            "Accept": "application/json"
        }
    });

    if (!response.ok) {
        throw new Error(`Services config load failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data || !Array.isArray(data.services)) {
        throw new Error("services.json must contain a services array");
    }

    return data.services;
}

function sanitizeService(service) {
    return {
        title: String(service.title || "Unnamed service"),
        description: String(service.description || service.info || ""),
        href: String(service.href || "#"),
        imageSrc: String(service.imageSrc || ""),
        placeholder: String(service.placeholder || getPlaceholderFromTitle(service.title || "Service"))
    };
}

function getPlaceholderFromTitle(title) {
    return String(title)
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0])
        .join("")
        .toUpperCase() || "SRV";
}

function createFallback(placeholder) {
    const fallback = document.createElement("div");

    fallback.className = "service-fallback";
    fallback.setAttribute("aria-hidden", "true");
    fallback.textContent = placeholder;

    return fallback;
}

function createImage(service) {
    const wrapper = document.createElement("div");

    wrapper.className = "service-image";

    if (!service.imageSrc) {
        wrapper.appendChild(createFallback(service.placeholder));
        return wrapper;
    }

    const image = document.createElement("img");

    image.src = service.imageSrc;
    image.alt = service.title;
    image.loading = "lazy";

    image.addEventListener("error", () => {
        wrapper.replaceChildren(createFallback(service.placeholder));
    });

    wrapper.appendChild(image);

    return wrapper;
}

function createInfoControl(service) {
    if (!service.description) {
        return null;
    }

    const infoButton = document.createElement("button");

    infoButton.type = "button";
    infoButton.className = "service-info-btn";
    infoButton.setAttribute("aria-label", `More information about ${service.title}`);
    infoButton.setAttribute("aria-expanded", "false");
    infoButton.textContent = "i";

    const popover = document.createElement("div");

    popover.className = "service-popover";
    popover.setAttribute("role", "tooltip");
    popover.hidden = true;
    popover.textContent = service.description;

    infoButton.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();

        const isOpen = !popover.hidden;

        closeAllPopovers();

        if (!isOpen) {
            popover.hidden = false;
            infoButton.setAttribute("aria-expanded", "true");
        }
    });

    return {
        infoButton,
        popover
    };
}

function closeAllPopovers() {
    if (!elements.servicesGrid) {
        return;
    }

    elements.servicesGrid.querySelectorAll(".service-popover").forEach((popover) => {
        popover.hidden = true;
    });

    elements.servicesGrid.querySelectorAll(".service-info-btn").forEach((button) => {
        button.setAttribute("aria-expanded", "false");
    });
}

function createServiceCard(rawService) {
    const service = sanitizeService(rawService);

    const card = document.createElement("article");
    card.className = "service-card";

    const imageLink = document.createElement("a");
    imageLink.className = "service-image-link";
    imageLink.href = service.href;
    imageLink.setAttribute("aria-label", `Open ${service.title}`);

    imageLink.appendChild(createImage(service));

    const info = document.createElement("div");
    info.className = "service-info";

    const titleLink = document.createElement("a");
    titleLink.className = "service-title-link";
    titleLink.href = service.href;

    const title = document.createElement("h3");
    title.textContent = service.title;

    titleLink.appendChild(title);
    info.appendChild(titleLink);

    const infoControl = createInfoControl(service);

    if (infoControl) {
        info.append(infoControl.infoButton, infoControl.popover);
    }

    card.append(imageLink, info);

    return card;
}

function renderServices(services) {
    if (!elements.servicesGrid) {
        return;
    }

    elements.servicesGrid.innerHTML = "";

    if (services.length === 0) {
        elements.servicesGrid.innerHTML = `<p class="services-message">No services configured.</p>`;
        return;
    }

    const fragment = document.createDocumentFragment();

    for (const service of services) {
        fragment.appendChild(createServiceCard(service));
    }

    elements.servicesGrid.appendChild(fragment);
}

function renderServicesError() {
    if (!elements.servicesGrid) {
        return;
    }

    elements.servicesGrid.innerHTML = `
        <p class="services-message services-message-error">
            Could not load services configuration.
        </p>
    `;
}

async function initServices() {
    try {
        const services = await loadServices();
        renderServices(services);
    } catch (error) {
        console.error(error);
        renderServicesError();
    }
}

document.addEventListener("click", closeAllPopovers);

initServices();