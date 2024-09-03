import React from 'react';

interface UserProfileProps {
  userProfile: {
    login: string;
    avatarUrl: string;
    createdAt: string;
    bio: string;
    followers: { totalCount: number };
    following: { totalCount: number };
  };
}

const UserProfile: React.FC<UserProfileProps> = ({ userProfile }) => {
  const yearsOnGithub = new Date().getFullYear() - new Date(userProfile.createdAt).getFullYear();

  return (
    <div className="bg-black text-white shadow-md flex items-center p-4">
      <div className="flex-shrink-0 mr-8">
        <img src={userProfile.avatarUrl} alt={`${userProfile.login}'s avatar`} className="w-32 h-32 rounded-full" />
      </div>
      <div className="flex-grow">
        <h1 className="text-5xl font-bold mb-4">{userProfile.login}</h1>
        <div className="flex space-x-12">
          <div className="space-y-2">
            <p>Followers: {userProfile.followers.totalCount}</p>
            <p>Following: {userProfile.following.totalCount}</p>
          </div>
          <div className="space-y-2">
            <p>{userProfile.bio || 'No bio available'}</p>
            <p># of years on Github: {yearsOnGithub}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
