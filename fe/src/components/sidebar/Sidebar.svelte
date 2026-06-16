<script lang="ts">
	import { page } from '$app/stores';
	import { mainMenuItems, masterMenuItems, poultryMenuItems, singleMenuItems } from './data';
	export let sidebarToggle: boolean;

	$: currentPath = $page.url.pathname;
</script>

<aside
	class={`sidebar fixed top-0 left-0 z-9999 flex h-screen w-[290px] flex-col overflow-y-hidden border-r border-gray-200 bg-white px-5 duration-300 ease-linear lg:static lg:translate-x-0 dark:border-gray-800 dark:bg-black ${sidebarToggle ? 'translate-x-0 lg:w-[90px]' : '-translate-x-full'}`}
>
	<!-- Sidebar Header -->
	<div
		class={`sidebar-header flex items-center gap-2 pt-8 pb-7 ${sidebarToggle ? 'justify-center' : 'justify-between'}`}
	>
		<a href="/">
			<span class={`logo ${sidebarToggle ? 'hidden' : ''}`}>
				<img class="dark:hidden" src="/logo/logo.svg" alt="Logo" />
				<img class="hidden dark:block" src="/logo/logo-dark.svg" alt="Logo" />
			</span>

			<img
				class={`logo-icon ${sidebarToggle ? 'lg:block' : 'hidden'}`}
				src="/logo/logo-icon.svg"
				alt="Logo"
			/>
		</a>
	</div>
	<!-- Sidebar Header -->

	<!-- Sidebar Menu -->
	<div class="no-scrollbar flex flex-col overflow-y-auto duration-300 ease-linear">
		<nav>
			<!-- Single Menu -->
			<ul class="mb-5 flex flex-col gap-3">
				{#each singleMenuItems as menu}
					<li>
						<a
							href={menu.link}
							class={`menu-item ${currentPath === menu.link ? 'menu-item-active' : 'menu-item-inactive'}`}
						>
							<menu.icon class="w-5 h-5" />

							<span class={`menu-item-text ${sidebarToggle ? 'lg:hidden' : ''}`}>{menu.label}</span>
						</a>
					</li>
				{/each}
			</ul>
			<!-- Main Menus -->
			<div>
				<h3 class="mb-3 text-xs leading-[20px] text-gray-400 uppercase">
					<span class={`menu-group-title ${sidebarToggle ? 'lg:hidden' : ''}`}>Main</span>

					<svg
						class={`menu-group-icon mx-auto fill-current ${sidebarToggle ? 'hidden lg:block' : 'hidden'}`}
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							fill-rule="evenodd"
							clip-rule="evenodd"
							d="M5.99915 10.2451C6.96564 10.2451 7.74915 11.0286 7.74915 11.9951V12.0051C7.74915 12.9716 6.96564 13.7551 5.99915 13.7551C5.03265 13.7551 4.24915 12.9716 4.24915 12.0051V11.9951C4.24915 11.0286 5.03265 10.2451 5.99915 10.2451ZM17.9991 10.2451C18.9656 10.2451 19.7491 11.0286 19.7491 11.9951V12.0051C19.7491 12.9716 18.9656 13.7551 17.9991 13.7551C17.0326 13.7551 16.2491 12.9716 16.2491 12.0051V11.9951C16.2491 11.0286 17.0326 10.2451 17.9991 10.2451ZM13.7491 11.9951C13.7491 11.0286 12.9656 10.2451 11.9991 10.2451C11.0326 10.2451 10.2491 11.0286 10.2491 11.9951V12.0051C10.2491 12.9716 11.0326 13.7551 11.9991 13.7551C12.9656 13.7551 13.7491 12.9716 13.7491 12.0051V11.9951Z"
							fill=""
						/>
					</svg>
				</h3>

				<ul class="mb-5 flex flex-col gap-3">
					{#each mainMenuItems as menu}
						<li>
							<a
								href={menu.link}
								class={`menu-item ${currentPath === menu.link ? 'menu-item-active' : 'menu-item-inactive'}`}
							>
								<menu.icon class="w-5 h-5" />

								<span class={`menu-item-text ${sidebarToggle ? 'lg:hidden' : ''}`}
									>{menu.label}</span
								>
							</a>
						</li>
					{/each}
				</ul>
			</div>
			<!-- Poultry Counter -->
			<div>
				<h3 class="mb-3 text-xs leading-[20px] text-gray-400 uppercase">
					<span class={`menu-group-title ${sidebarToggle ? 'lg:hidden' : ''}`}>POULTRY COUNTER</span>
					<svg
						class={`menu-group-icon mx-auto fill-current ${sidebarToggle ? 'hidden lg:block' : 'hidden'}`}
						width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
					>
						<path fill-rule="evenodd" clip-rule="evenodd" d="M5.99915 10.2451C6.96564 10.2451 7.74915 11.0286 7.74915 11.9951V12.0051C7.74915 12.9716 6.96564 13.7551 5.99915 13.7551C5.03265 13.7551 4.24915 12.9716 4.24915 12.0051V11.9951C4.24915 11.0286 5.03265 10.2451 5.99915 10.2451ZM17.9991 10.2451C18.9656 10.2451 19.7491 11.0286 19.7491 11.9951V12.0051C19.7491 12.9716 18.9656 13.7551 17.9991 13.7551C17.0326 13.7551 16.2491 12.9716 16.2491 12.0051V11.9951C16.2491 11.0286 17.0326 10.2451 17.9991 10.2451ZM13.7491 11.9951C13.7491 11.0286 12.9656 10.2451 11.9991 10.2451C11.0326 10.2451 10.2491 11.0286 10.2491 11.9951V12.0051C10.2491 12.9716 11.0326 13.7551 11.9991 13.7551C12.9656 13.7551 13.7491 12.9716 13.7491 12.0051V11.9951Z" fill="" />
					</svg>
				</h3>
				<ul class="mb-5 flex flex-col gap-3">
					{#each poultryMenuItems as menu}
						<li>
							<a
								href={menu.link}
								class={`menu-item ${currentPath === menu.link ? 'menu-item-active' : 'menu-item-inactive'}`}
							>
								<menu.icon class="w-5 h-5" />
								<span class={`menu-item-text ${sidebarToggle ? 'lg:hidden' : ''}`}>{menu.label}</span>
							</a>
						</li>
					{/each}
				</ul>
			</div>
			<!-- Master Menus -->
			<div>
				<h3 class="mb-3 text-xs leading-[20px] text-gray-400 uppercase">
					<span class={`menu-group-title ${sidebarToggle ? 'lg:hidden' : ''}`}>MANAGEMENT</span>

					<svg
						class={`menu-group-icon mx-auto fill-current ${sidebarToggle ? 'hidden lg:block' : 'hidden'}`}
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							fill-rule="evenodd"
							clip-rule="evenodd"
							d="M5.99915 10.2451C6.96564 10.2451 7.74915 11.0286 7.74915 11.9951V12.0051C7.74915 12.9716 6.96564 13.7551 5.99915 13.7551C5.03265 13.7551 4.24915 12.9716 4.24915 12.0051V11.9951C4.24915 11.0286 5.03265 10.2451 5.99915 10.2451ZM17.9991 10.2451C18.9656 10.2451 19.7491 11.0286 19.7491 11.9951V12.0051C19.7491 12.9716 18.9656 13.7551 17.9991 13.7551C17.0326 13.7551 16.2491 12.9716 16.2491 12.0051V11.9951C16.2491 11.0286 17.0326 10.2451 17.9991 10.2451ZM13.7491 11.9951C13.7491 11.0286 12.9656 10.2451 11.9991 10.2451C11.0326 10.2451 10.2491 11.0286 10.2491 11.9951V12.0051C10.2491 12.9716 11.0326 13.7551 11.9991 13.7551C12.9656 13.7551 13.7491 12.9716 13.7491 12.0051V11.9951Z"
							fill=""
						/>
					</svg>
				</h3>

				<ul class="mb-5 flex flex-col gap-3">
					{#each masterMenuItems as menu}
						<li>
							<a
								href={menu.link}
								class={`menu-item ${currentPath === menu.link ? 'menu-item-active' : 'menu-item-inactive'}`}
							>
								<menu.icon class="w-5 h-5" />

								<span class={`menu-item-text ${sidebarToggle ? 'lg:hidden' : ''}`}>{menu.label}</span>
							</a>
						</li>
					{/each}
				</ul>
			</div>
		</nav>
	</div>
	<!-- Sidebar Menu -->
</aside>
